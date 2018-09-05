# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import confluent_kafka
import imp
import inspect
import os
import threading
import time
from xosconfig import Config
from multistructlog import create_logger

log = create_logger(Config().get('logging'))


class XOSKafkaThread(threading.Thread):
    """ XOSKafkaThread

        A Thread for servicing Kafka events. There is one event_step associated with one XOSKafkaThread. A
        Consumer is launched to listen on the topics specified by the thread. The thread's process_event()
        function is called for each event.
    """

    def __init__(self, step, bootstrap_servers, *args, **kwargs):
        super(XOSKafkaThread, self).__init__(*args, **kwargs)
        self.consumer = None
        self.step = step
        self.bootstrap_servers = bootstrap_servers
        self.daemon = True

    def create_kafka_consumer(self):
        consumer_config = {
            'bootstrap.servers': ','.join(self.bootstrap_servers),
        }

        return confluent_kafka.Consumer(**consumer_config)

    def run(self):
        if (not self.step.topics) and (not self.step.pattern):
            raise Exception("Neither topics nor pattern is defined for step %s" % self.step.__name__)

        if self.step.topics and self.step.pattern:
            raise Exception("Both topics and pattern are defined for step %s. Choose one." %
                            self.step.__name__)

        while True:
            try:
                self.consumer = self.create_kafka_consumer()
                if self.step.topics:
                    self.consumer.subscribe(self.step.topics)
                elif self.step.pattern:
                    self.consumer.subscribe(self.step.pattern)

                log.info("Waiting for events",
                         topic=self.step.topics,
                         pattern=self.step.pattern,
                         step=self.step.__name__)

                for msg in self.consumer.poll():
                    log.info("Processing event", msg=msg, step=self.step.__name__)
                    try:
                        self.step(log=log).process_event(msg)
                    except:
                        log.exception("Exception in event step", msg=msg, step=self.step.__name__)

            except confluent_kafka.KafkaError._ALL_BROKERS_DOWN, e:
                log.warning("No brokers available on %s, %s" % (self.bootstrap_servers, e))
                time.sleep(20)
            except confluent_kafka.KafkaError, e:
                # Maybe Kafka has not started yet. Log the exception and try again in a second.
                log.exception("Exception in kafka loop: %s" % e)
                time.sleep(1)

class XOSEventEngine:
    """ XOSEventEngine

        Subscribe to and handle processing of events. Two methods are defined:

            load_step_modules(dir) ... look for step modules in the given directory, and load objects that are
                                       descendant from EventStep.

            start() ... Launch threads to handle processing of the EventSteps. It's expected that load_step_modules()
                        will be called before start().
    """

    def __init__(self):
        self.event_steps = []
        self.threads = []

    def load_event_step_modules(self, event_step_dir):
        self.event_steps = []
        log.info("Loading event steps", event_step_dir=event_step_dir)

        # NOTE we'll load all the classes that inherit from EventStep
        for fn in os.listdir(event_step_dir):
            pathname = os.path.join(event_step_dir, fn)
            if os.path.isfile(pathname) and fn.endswith(".py") and (fn != "__init__.py") and ("test" not in fn):
                event_module = imp.load_source(fn[:-3], pathname)

                for classname in dir(event_module):
                    c = getattr(event_module, classname, None)

                    if inspect.isclass(c):
                        base_names = [b.__name__ for b in c.__bases__]
                        if 'EventStep' in base_names:
                            self.event_steps.append(c)
        log.info("Loaded event steps", steps=self.event_steps)

    def start(self):
        eventbus_kind = Config.get("event_bus.kind")
        eventbus_endpoint = Config.get("event_bus.endpoint")

        if not eventbus_kind:
            log.error("Eventbus kind is not configured in synchronizer config file.")
            return

        if eventbus_kind not in ["kafka"]:
            log.error("Eventbus kind is set to a technology we do not implement.", eventbus_kind=eventbus_kind)
            return

        if not eventbus_endpoint:
            log.error("Eventbus endpoint is not configured in synchronizer config file.")
            return

        for step in self.event_steps:
            if step.technology == "kafka":
                thread = XOSKafkaThread(step=step, bootstrap_servers=[eventbus_endpoint])
                thread.start()
                self.threads.append(thread)
            else:
                log.error("Unknown technology. Skipping step", technology=step.technology, step=step.__name__)
