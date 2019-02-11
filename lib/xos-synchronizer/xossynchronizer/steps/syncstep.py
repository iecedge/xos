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


import os
import base64

from xosconfig import Config
from xossynchronizer.modelaccessor import *
from xossynchronizer.ansible_helper import run_template

# from tests.steps.mock_modelaccessor import model_accessor

import json
import time
import pdb

from xosconfig import Config
from functools import reduce


def f7(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def elim_dups(backend_str):
    strs = backend_str.split(" // ")
    strs2 = f7(strs)
    return " // ".join(strs2)


def deepgetattr(obj, attr):
    return reduce(getattr, attr.split("."), obj)


def obj_class_name(obj):
    return getattr(obj, "model_name", obj.__class__.__name__)


class InnocuousException(Exception):
    pass


class DeferredException(Exception):
    pass


class FailedDependency(Exception):
    pass


class SyncStep(object):
    """ An XOS Sync step.

    Attributes:
        psmodel        Model name the step synchronizes
        dependencies    list of names of models that must be synchronized first if the current model depends on them
    """

    # map_sync_outputs can return this value to cause a step to be marked
    # successful without running ansible. Used for sync_network_controllers
    # on nat networks.
    SYNC_WITHOUT_RUNNING = "sync_without_running"

    slow = False

    def get_prop(self, prop):
        # NOTE config_dir is never define, is this used?
        sync_config_dir = Config.get("config_dir")
        prop_config_path = "/".join(sync_config_dir, self.name, prop)
        return open(prop_config_path).read().rstrip()

    def __init__(self, **args):
        """Initialize a sync step
           Keyword arguments:
                   name -- Name of the step
                provides -- XOS models sync'd by this step
        """
        dependencies = []
        self.driver = args.get("driver")
        self.error_map = args.get("error_map")

        try:
            self.soft_deadline = int(self.get_prop("soft_deadline_seconds"))
        except BaseException:
            self.soft_deadline = 5  # 5 seconds

        if "log" in args:
            self.log = args.get("log")

        return

    def fetch_pending(self, deletion=False):
        # This is the most common implementation of fetch_pending
        # Steps should override it if they have their own logic
        # for figuring out what objects are outstanding.

        return model_accessor.fetch_pending(self.observes, deletion)

    def sync_record(self, o):
        self.log.debug("In default sync record", **o.tologdict())

        tenant_fields = self.map_sync_inputs(o)
        if tenant_fields == SyncStep.SYNC_WITHOUT_RUNNING:
            return

        main_objs = self.observes
        if isinstance(main_objs, list):
            main_objs = main_objs[0]

        path = "".join(main_objs.__name__).lower()
        res = run_template(self.playbook, tenant_fields, path=path, object=o)

        if hasattr(self, "map_sync_outputs"):
            self.map_sync_outputs(o, res)

        self.log.debug("Finished default sync record", **o.tologdict())

    def delete_record(self, o):
        self.log.debug("In default delete record", **o.tologdict())

        # If there is no map_delete_inputs, then assume deleting a record is a no-op.
        if not hasattr(self, "map_delete_inputs"):
            return

        tenant_fields = self.map_delete_inputs(o)

        main_objs = self.observes
        if isinstance(main_objs, list):
            main_objs = main_objs[0]

        path = "".join(main_objs.__name__).lower()

        tenant_fields["delete"] = True
        res = run_template(self.playbook, tenant_fields, path=path)

        if hasattr(self, "map_delete_outputs"):
            self.map_delete_outputs(o, res)
        else:
            # "rc" is often only returned when something bad happens, so assume that no "rc" implies a successful rc
            # of 0.
            if res[0].get("rc", 0) != 0:
                raise Exception("Nonzero rc from Ansible during delete_record")

        self.log.debug("Finished default delete record", **o.tologdict())
