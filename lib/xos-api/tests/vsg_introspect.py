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
from xosapi import xos_grpc_client
import sys

sys.path.append("..")


def test_callback():
    print("TEST: vsg_introspect")

    c = xos_grpc_client.coreclient

    for vsg in c.xos_orm.VSGTenant.objects.all():
        print("  vsg", vsg.id)
        for field_name in [
            "wan_container_ip",
            "wan_container_mac",
            "wan_container_netbits",
            "wan_container_gateway_ip",
            "wan_container_gateway_mac",
            "wan_vm_ip",
            "wan_vm_mac",
        ]:
            print("    %s: %s" % (field_name, getattr(vsg, field_name)))

    print("    okay")


xos_grpc_client.start_api_parseargs(test_callback)
