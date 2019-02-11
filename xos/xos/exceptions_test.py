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


from xos.exceptions import *
import xos.exceptions
import unittest
import sys
import os
import inspect
import json

sys.path.append(os.path.abspath(".."))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")


class TestXosExceptions(unittest.TestCase):
    """
    Test the conversion from excenption to json
    """

    def test_get_json_error_details(self):
        res = xos.exceptions._get_json_error_details({"foo": "bar"})
        assert res == json.dumps({"foo": "bar"})

    def test_exceptions(self):
        """
        This test iterate over all the classes in exceptions.py and if they start with XOS
         validate the json_detail output
        """
        for name, item in inspect.getmembers(xos.exceptions):
            if inspect.isclass(item) and name.startswith("XOS"):
                e = item("test error", {"foo": "bar"})
                res = e.json_detail
                assert res == json.dumps(
                    {
                        "fields": {"foo": "bar"},
                        "specific_error": "test error",
                        "error": name,
                    }
                )


if __name__ == "__main__":
    unittest.main()
