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
from xosgenx.generator import XOSProcessor, XOSProcessorArgs
from helpers import FakeObject, XProtoTestHelpers
import pdb

"""
The tests below convert the policy logic expression
into Python, set up an appropriate environment and execute the Python.
"""


class XProtoPolicyTest(unittest.TestCase):
    def test_annotation(self):
        xproto = """
    policy true_policy < True >

    message always::true_policy {
        required int still = 9;
    }
"""

        target = XProtoTestHelpers.write_tmp_target("{{ proto.messages.0 }}")

        args = XOSProcessorArgs()
        args.inputs = xproto
        args.target = target

        output = XOSProcessor.process(args)
        self.assertIn("true_policy", output)

    def test_constant(self):
        xproto = """
    policy true_policy < True >
"""

        target = XProtoTestHelpers.write_tmp_target("{{ proto.policies.true_policy }}")

        args = XOSProcessorArgs()
        args.inputs = xproto
        args.target = target

        output = XOSProcessor.process(args).replace("t", "T")
        self.assertTrue(eval(output))

    def test_function_term(self):
        xproto = """
    policy slice_user < slice.user.compute_is_admin() >
"""

        target = XProtoTestHelpers.write_tmp_target("{{ proto.policies.slice_user }}")
        args = XOSProcessorArgs()
        args.inputs = xproto
        args.target = target

        output = XOSProcessor.process(args)

        slice = FakeObject()
        slice.user = FakeObject()
        slice.user.compute_is_admin = lambda: True

        expr = eval(output)
        self.assertTrue(expr)

    def test_term(self):
        xproto = """
    policy slice_user < slice.user.is_admin >
"""

        target = XProtoTestHelpers.write_tmp_target("{{ proto.policies.slice_user }}")
        args = XOSProcessorArgs()
        args.inputs = xproto
        args.target = target

        output = XOSProcessor.process(args)

        slice = FakeObject()
        slice.user = FakeObject()
        slice.user.is_admin = True

        expr = eval(output)
        self.assertTrue(expr)

    def test_num_constant(self):
        xproto = """
    policy slice_user < slice.user.age = 57 >
"""

        target = XProtoTestHelpers.write_tmp_target("{{ proto.policies.slice_user }}")
        args = XOSProcessorArgs()
        args.inputs = xproto
        args.target = target

        output = XOSProcessor.process(args)

        slice = FakeObject()
        slice.user = FakeObject()
        slice.user.is_admin = True

        expr = eval(output)
        self.assertTrue(expr)

    def test_string_constant(self):
        xproto = """
    policy slice_user < slice.user.email = "admin@opencord.org" >
"""

        target = XProtoTestHelpers.write_tmp_target("{{ proto.policies.slice_user }}")
        args = XOSProcessorArgs()
        args.inputs = xproto
        args.target = target

        output = XOSProcessor.process(args)

        slice = FakeObject()
        slice.user = FakeObject()
        slice.user.is_admin = True

        expr = eval(output)
        self.assertTrue(expr)

    def test_equal(self):
        xproto = """
    policy slice_user < slice.user = obj.user >
"""

        target = XProtoTestHelpers.write_tmp_target("{{ proto.policies.slice_user }}")
        args = XOSProcessorArgs()
        args.inputs = xproto
        args.target = target

        output = XOSProcessor.process(args)

        slice = FakeObject()
        slice.user = "twin"
        obj = FakeObject()
        obj.user = "twin"

        (op, operands), = eval(output).items()
        expr = op.join(operands).replace("=", "==")

        self.assertTrue(eval(expr))

    def test_bin(self):
        xproto = """
    policy slice_admin < slice.is_admin | obj.empty >
"""
        target = XProtoTestHelpers.write_tmp_target("{{ proto.policies.slice_admin }}")
        args = XOSProcessorArgs()
        args.inputs = xproto
        args.target = target

        output = XOSProcessor.process(args)

        slice = FakeObject()
        slice.is_admin = False
        obj = FakeObject()
        obj.empty = []

        (op, operands), = eval(output).items()
        expr = op.join(operands).replace("|", " or ")

        self.assertFalse(eval(expr))

    def test_implies(self):
        xproto = """
    policy implies < obj.name -> obj.creator >
"""
        target = XProtoTestHelpers.write_tmp_target("{{ proto.policies.implies }}")
        args = XOSProcessorArgs()
        args.inputs = xproto
        args.target = target

        output = XOSProcessor.process(args)

        slice = FakeObject()
        slice.is_admin = False
        obj = FakeObject()
        obj.name = "Thing 1"
        obj.creator = None

        (op, operands), = eval(output).items()
        expr = "not " + op.join(operands).replace("->", " or ")

        self.assertFalse(eval(expr))

    def test_exists(self):
        xproto = """
    policy privilege < exists Privilege: Privilege.object_id = obj.id >
"""

        target = XProtoTestHelpers.write_tmp_target("{{ proto.policies.privilege }} ")
        args = XOSProcessorArgs()
        args.inputs = xproto
        args.target = target

        output = XOSProcessor.process(args)

        Privilege = FakeObject()
        Privilege.object_id = 1
        obj = FakeObject()
        obj.id = 1

        (op, operands), = eval(output).items()
        (op2, operands2), = operands[1].items()
        expr = op2.join(operands2).replace("=", "==")

        self.assertTrue(eval(expr))

    def test_policy_function(self):
        xproto = """
    policy slice_policy < exists Privilege: Privilege.object_id = obj.id >
    policy network_slice_policy < *slice_policy(slice) >
"""

        target = XProtoTestHelpers.write_tmp_target(
            "{{ proto.policies.network_slice_policy }} "
        )
        args = XOSProcessorArgs()
        args.inputs = xproto
        args.target = target

        output = XOSProcessor.process(args)

        (op, operands), = eval(output).items()

        self.assertIn("slice_policy", operands)
        self.assertIn("slice", operands)

    def test_policy_missing_function(self):
        xproto = """
    policy slice_policy < exists Privilege: Privilege.object_id = obj.id >
    policy network_slice_policy < *slice_policyX(slice) >
"""

        target = XProtoTestHelpers.write_tmp_target(
            "{{ proto.policies.network_slice_policy }} "
        )
        args = XOSProcessorArgs()
        args.inputs = xproto
        args.target = target

        with self.assertRaises(Exception):
            output = XOSProcessor.process(args)

    def test_forall(self):
        # This one we only parse
        xproto = """
    policy instance < forall Instance: exists Credential: Credential.obj_id = Instance.obj_id >
"""

        target = XProtoTestHelpers.write_tmp_target("{{ proto.policies.instance }}")

        args = XOSProcessorArgs()
        args.inputs = xproto
        args.target = target

        output = XOSProcessor.process(args)
        (op, operands), = eval(output).items()

        self.assertEqual(op, "forall")


if __name__ == "__main__":
    unittest.main()
