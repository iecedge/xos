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


import unittest
import os
from mock import patch
from xosgenx.xosgen import XosGen


class Args:
    pass


class XOSProcessorTest(unittest.TestCase):
    """
    Testing the CLI binding for the XOS Generative Toolchain
    """

    def setUp(self):
        os.chdir(
            os.path.join(
                os.path.abspath(os.path.dirname(os.path.realpath(__file__))), ".."
            )
        )

    def test_generator(self):
        """
        [XOS-GenX] The CLI entry point should correctly parse params
        """
        args = Args()
        args.files = ["xos-genx-tests/xproto/test.xproto"]
        args.target = "xos-genx-tests/xtarget/test.xtarget"
        args.output = "xos-genx-tests/out/dir/"
        args.write_to_file = "target"
        args.dest_file = None
        args.dest_extension = None

        expected_args = Args()
        expected_args.files = [os.path.abspath(os.getcwd() + "/" + args.files[0])]
        expected_args.target = os.path.abspath(os.getcwd() + "/" + args.target)
        expected_args.output = os.path.abspath(os.getcwd() + "/" + args.output)

        with patch("xosgenx.xosgen.XOSProcessor.process") as generator:
            XosGen.init(args)
            actual_args = generator.call_args[0][0]
            self.assertEqual(actual_args.files, expected_args.files)
            self.assertEqual(actual_args.output, expected_args.output)


if __name__ == "__main__":
    unittest.main()
