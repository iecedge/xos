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


#! /usr/bin/env python

from __future__ import print_function
import json
import os
import requests
import sys

REST_API = "http://alpha.opencloud.us:8000/xos/"

NODES_API = REST_API + "nodes/"
SLICES_API = REST_API + "slices/"
SLIVERS_API = REST_API + "instances/"

opencloud_auth = ("demo@onlab.us", "demo")


def get_slice_id(slice_name):
    r = requests.get(SLICES_API + "?name=%s" % slice_name, auth=opencloud_auth)
    return r.json()[0]["id"]


def get_node_id(host_name):
    r = requests.get(NODES_API)
    nodes = r.json()
    for node in nodes:
        if node["name"].lower() == host_name.lower():
            return node["id"]
    print("Error: failed to find node %s" % host_name, file=sys.stderr)
    sys.exit(-1)


def get_instances(slice_id=None, node_id=None):
    queries = []
    if slice_id:
        queries.append("slice=%s" % str(slice_id))
    if node_id:
        queries.append("node=%s" % str(node_id))

    if queries:
        query_string = "?" + "&".join(queries)
    else:
        query_string = ""

    r = requests.get(SLIVERS_API + query_string, auth=opencloud_auth)
    return r.json()


def main():
    global opencloud_auth

    if len(sys.argv) != 5:
        print(
            "syntax: get_instance_name.py <username>, <password>, <hostname> <slicename>",
            file=sys.stderr,
        )
        sys.exit(-1)

    username = sys.argv[1]
    password = sys.argv[2]
    hostname = sys.argv[3]
    slice_name = sys.argv[4]

    opencloud_auth = (username, password)

    slice_id = get_slice_id(slice_name)
    node_id = get_node_id(hostname)
    instances = get_instances(slice_id, node_id)

    instance_names = [x["instance_name"] for x in instances if x["instance_name"]]

    # return the last one in the list (i.e. the newest one)

    print(sorted(instance_names)[-1])


if __name__ == "__main__":
    main()
