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

from __future__ import print_function
import exceptions
import os
import random
import string
import sys
import unittest

# Command-line argument of -R will cause this test to use a real grpc server
# rather than the fake stub.

# TODO: Investigate writing wrapper unit tests using mocks rather than using the ORM test framework

# by default, use fake stub rather than real core
USE_FAKE_STUB = True

PARENT_DIR = os.path.join(os.path.dirname(__file__), "..")


class TestWrappers(unittest.TestCase):
    def setUp(self):
        from xosconfig import Config

        test_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
        config = os.path.join(test_path, "test_config.yaml")
        Config.clear()
        Config.init(config, "synchronizer-config-schema.yaml")

        if USE_FAKE_STUB:
            sys.path.append(PARENT_DIR)

    def tearDown(self):
        if USE_FAKE_STUB:
            sys.path.remove(PARENT_DIR)

    def make_coreapi(self):
        if USE_FAKE_STUB:
            import xosapi.orm
            from fake_stub import FakeStub, FakeObj, FakeProtos

            xosapi.orm.import_convenience_methods()

            stub = FakeStub()
            api = xosapi.orm.ORMStub(
                stub=stub,
                package_name="xos",
                protos=FakeProtos(),
                empty=FakeObj,
                enable_backoff=False,
            )
            return api
        else:
            return xos_grpc_client.coreapi

    def test_service_get_composable_networks(self):
        orm = self.make_coreapi()
        deployment = orm.Deployment(name="test_deployment")
        deployment.save()
        controller = orm.Controller(name="test_controller", deployment_id=deployment.id)
        controller.save()
        site = orm.Site(name="testsite")
        site.save()
        user = orm.User(
            email="fake_"
            + "".join(
                random.choice(string.ascii_uppercase + string.digits) for _ in range(10)
            ),
            site_id=site.id,
        )
        user.save()
        vsg_access_template = orm.NetworkTemplate(name="vsg_access", vtn_kind="VSG")
        vsg_access_template.save()
        service_one = orm.Service(name="service_one")
        service_one.save()
        slice_one = orm.Slice(
            name="testsite_sliceone",
            service_id=service_one.id,
            site_id=site.id,
            creator_id=user.id,
            network="noauto",
        )
        slice_one.save()
        network_one = orm.Network(
            name="testsite_sliceone_access",
            owner_id=slice_one.id,
            template_id=vsg_access_template.id,
        )
        network_one.save()
        ns = orm.NetworkSlice(slice_id=slice_one.id, network_id=network_one.id)
        ns.save()
        cn_one = orm.ControllerNetwork(
            network_id=network_one.id, controller_id=controller.id
        )
        cn_one.save()

        if USE_FAKE_STUB:
            # fake_Stub doesn't handle reverse foreign keys
            service_one.slices_ids = [slice_one.id]
            slice_one.networks_ids = [network_one.id]
            network_one.controllernetworks_ids = [cn_one.id]

        # make sure we're using a fresh copy of the object, with all its foreign keys filled in
        service_one = orm.Service.objects.get(id=service_one.id)

        cns = service_one.get_composable_networks()
        self.assertEqual(len(cns), 1)
        self.assertEqual(cns[0].id, network_one.id)

    def test_service_get_service_instance_class_name(self):
        orm = self.make_coreapi()
        deployment = orm.Deployment(name="test_deployment")
        deployment.save()
        controller = orm.Controller(name="test_controller", deployment_id=deployment.id)
        controller.save()
        site = orm.Site(name="testsite")
        site.save()
        user = orm.User(
            email="fake_"
            + "".join(
                random.choice(string.ascii_uppercase + string.digits) for _ in range(10)
            ),
            site_id=site.id,
        )
        user.save()
        vsg_access_template = orm.NetworkTemplate(name="vsg_access", vtn_kind="VSG")
        vsg_access_template.save()
        service_one = orm.Service(name="service_one")
        service_one.save()

        self.assertEqual(
            service_one.get_service_instance_class_name(), "ServiceInstance"
        )

    def test_service_get_service_instance_class(self):
        orm = self.make_coreapi()
        deployment = orm.Deployment(name="test_deployment")
        deployment.save()
        controller = orm.Controller(name="test_controller", deployment_id=deployment.id)
        controller.save()
        site = orm.Site(name="testsite")
        site.save()
        user = orm.User(
            email="fake_"
            + "".join(
                random.choice(string.ascii_uppercase + string.digits) for _ in range(10)
            ),
            site_id=site.id,
        )
        user.save()
        vsg_access_template = orm.NetworkTemplate(name="vsg_access", vtn_kind="VSG")
        vsg_access_template.save()
        service_one = orm.Service(name="service_one")
        service_one.save()

        self.assertEqual(
            service_one.get_service_instance_class().model_name, "ServiceInstance"
        )

    def test_wrapper_from__class__dot_name(self):
        """ The Service model has a wrapper, so it should be returned when make_ORMWrapper looks for a wrapper based
            on the class name.
        """
        orm = self.make_coreapi()
        obj = orm.Service()
        self.assertEqual(obj.__class__.__name__, "ORMWrapperService")

    def test_wrapper_from_class_names(self):
        """ ONOSService._wrapped_class.class_names is "ONOSService, Service" so we should fall back to getting the
            Service wrapper.
        """
        orm = self.make_coreapi()
        obj = orm.ONOSService()
        self.assertEqual(obj.__class__.__name__, "ORMWrapperService")


def main():
    global USE_FAKE_STUB
    global xos_grpc_client

    # Command-line argument of -R will cause this test to use a real grpc server
    # rather than the fake stub.

    if "-R" in sys.argv:
        USE_FAKE_STUB = False
        sys.argv.remove("-R")
        # Note: will leave lots of litter (users, sites, etc) behind in the database

    if USE_FAKE_STUB:
        unittest.main()
    else:
        # This assumes xos-client python library is installed, and a gRPC server
        # is available.

        from xosapi import xos_grpc_client

        print("Using xos-client library and core server")

        def test_callback():
            try:
                sys.argv = sys.argv[
                    :1
                ]  # unittest does not like xos_grpc_client's command line arguments (TODO: find a cooperative approach)
                unittest.main()
            except exceptions.SystemExit as e:
                global exitStatus
                exitStatus = e.code

        xos_grpc_client.start_api_parseargs(test_callback)

        sys.exit(exitStatus)


if __name__ == "__main__":
    main()
