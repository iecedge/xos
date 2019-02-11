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


from base import *
import pdb
import re


def django_content_type_string(xptags):
    # Check possibility of KeyError in caller
    content_type = xptags["content_type"]

    try:
        content_type = eval(content_type)
    except BaseException:
        pass

    if content_type == "url":
        return "URLField"
    if content_type == "date":
        return "DateTimeField"
    elif content_type == "ip":
        return "GenericIPAddressField"
    elif content_type == "stripped" or content_type == '"stripped"':
        return "StrippedCharField"
    else:
        raise Exception("Unknown Type: %s" % content_type)


def django_string_type(xptags):
    try:
        max_length = eval(xptags["max_length"])
    except BaseException:
        max_length = 1024 * 1024

    if "content_type" in xptags:
        return django_content_type_string(xptags)
    elif max_length < 1024 * 1024:
        return "CharField"
    else:
        return "TextField"


def xproto_django_type(xptype, xptags):
    if xptype == "string":
        return django_string_type(xptags)
    elif xptype == "float":
        return "FloatField"
    elif xptype == "bool":
        return "BooleanField"
    elif xptype == "uint32":
        return "IntegerField"
    elif xptype == "int32":
        return "IntegerField"
    elif xptype == "int64":
        return "BigIntegerField"
    else:
        raise Exception("Unknown Type: %s" % xptype)


def xproto_django_link_type(f):
    if f["link_type"] == "manytoone":
        return "ForeignKey"
    elif f["link_type"] == "onetoone":
        return "OneToOneField"
    elif f["link_type"] == "manytomany":
        if f["dst_port"]:
            return "ManyToManyField"
        else:
            return "GenericRelation"


def map_xproto_to_django(f):
    allowed_keys = [
        "help_text",
        "default",
        "max_length",
        "modifier",
        "blank",
        "choices",
        "db_index",
        "null",
        "editable",
        "on_delete",
        "verbose_name",
        "auto_now_add",
        "unique",
        "min_value",
        "max_value",
    ]

    # TODO evaluate if setting Null = False for all strings
    m = {
        "modifier": {"optional": True, "required": False, "_targets": ["null", "blank"]}
    }
    out = {}

    for k, v in f["options"].items():
        if k in allowed_keys:
            try:
                # NOTE this will be used to parse xproto optional/required field prefix
                # and apply it to the null and blank fields
                kv2 = m[k]
                for t in kv2["_targets"]:
                    out[t] = kv2[v]
            except BaseException:
                out[k] = v

    return out


def xproto_django_link_options_str(field, dport=None):
    output_dict = map_xproto_to_django(field)

    if dport and (dport == "+" or "+" not in dport):
        output_dict["related_name"] = "%r" % dport

    try:
        if field["through"]:
            d = {}
            if isinstance(field["through"], str):
                split = field["through"].rsplit(".", 1)
                d["name"] = split[-1]
                if len(split) == 2:
                    d["package"] = split[0]
                    d["fqn"] = "package" + "." + d["name"]
                else:
                    d["fqn"] = d["name"]
                    d["package"] = ""
            else:
                d = field["through"]

            if not d["name"].endswith("_" + field["name"]):
                output_dict["through"] = "%r" % d["fqn"]
    except KeyError:
        pass

    return format_options_string(output_dict)


def use_native_django_validators(k, v):

    validators_map = {
        "min_value": "MinValueValidator",
        "max_value": "MaxValueValidator",
    }

    return "%s(%s)" % (validators_map[k], v)


def format_options_string(d):

    known_validators = ["min_value", "max_value"]
    validator_lst = []

    if not d:
        return ""
    else:

        lst = []
        for k, v in d.items():
            if k in known_validators:
                validator_lst.append(use_native_django_validators(k, v))
            elif isinstance(v, str) and k == "default" and v.endswith('()"'):
                lst.append("%s = %s" % (k, v[1:-3]))
            elif isinstance(v, str) and v.startswith('"'):
                try:
                    # unquote the value if necessary
                    tup = eval(v[1:-1])
                    if isinstance(tup, tuple):
                        lst.append("%s = %r" % (k, tup))
                    else:
                        lst.append("%s = %s" % (k, v))
                except BaseException:
                    lst.append("%s = %s" % (k, v))
            elif isinstance(v, bool):
                lst.append("%s = %r" % (k, bool(v)))
            else:
                try:
                    lst.append("%s = %r" % (k, int(v)))
                except ValueError:
                    lst.append("%s = %s" % (k, v))
        validator_string = "validators=[%s]" % ", ".join(validator_lst)
        option_string = ", ".join(lst)
        if len(validator_lst) == 0:
            return option_string
        elif len(lst) == 0:
            return validator_string
        else:
            return option_string + ", " + validator_string


def xproto_django_options_str(field, dport=None):
    output_dict = map_xproto_to_django(field)

    if dport == "_":
        dport = "+"

    if dport and (dport == "+" or "+" not in dport):
        output_dict["related_name"] = "%r" % dport

    return format_options_string(output_dict)


def xproto_camel_to_underscore(name):
    return re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)


def xproto_validations(options):
    try:
        return [
            map(str.strip, validation.split(":"))
            for validation in unquote(options["validators"]).split(",")
        ]
    except KeyError:
        return []


def xproto_optioned_fields_to_list(fields, option, val):
    """
    List all the field that have a particural option
    :param fields: (list) an array of message fields
    :param option: (string) the option to look for
    :param val: (any) the value of the option
    :return: list of strings, field names where option is set
    """

    optioned_fields = []
    for f in fields:
        option_names = []
        for k, v in f["options"].items():
            option_names.append(k)

        if option in option_names and f["options"][option] == val:
            optioned_fields.append(f["name"])

    return optioned_fields


# TODO
# - in modeldefs add info about this fields
# - update the gui to have this fields as readonly
