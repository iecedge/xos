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

import inspect
from apistats import REQUEST_COUNT, track_request_time
import grpc
from apihelper import XOSAPIHelperMixin, translate_exceptions
from xos.exceptions import XOSNotAuthenticated
from core.models import ServiceInstance
from django.db.models import F, Q
import django.apps
from django.contrib.auth import authenticate as django_authenticate
import fnmatch
import os
import sys
import traceback
from protos import utility_pb2, utility_pb2_grpc
from google.protobuf.empty_pb2 import Empty

from importlib import import_module
from django.conf import settings

SessionStore = import_module(settings.SESSION_ENGINE).SessionStore


# The Tosca engine expects to be run from /opt/xos/tosca/ or equivalent. It
# needs some sys.path fixing up.

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
toscadir = os.path.join(currentdir, "../tosca")


def is_internal_model(model):
    """ things to be excluded from the dirty_models endpoints """
    if "django" in model.__module__:
        return True
    if "cors" in model.__module__:
        return True
    if "contenttypes" in model.__module__:
        return True
    if "core.models.journal" in model.__module__:  # why?
        return True
    if "core.models.project" in model.__module__:  # why?
        return True
    return False


def get_xproto(folder):
    matches = []
    for root, dirnames, filenames in os.walk(folder):
        for filename in fnmatch.filter(filenames, "*.xproto"):
            matches.append(os.path.join(root, filename))
    return matches


class UtilityService(utility_pb2_grpc.utilityServicer, XOSAPIHelperMixin):
    def __init__(self, thread_pool):
        self.thread_pool = thread_pool
        XOSAPIHelperMixin.__init__(self)

    def stop(self):
        pass

    @translate_exceptions("Utilities", "Login")
    @track_request_time("Utilities", "Login")
    def Login(self, request, context):
        if not request.username:
            raise XOSNotAuthenticated("No username")

        u = django_authenticate(username=request.username, password=request.password)
        if not u:
            raise XOSNotAuthenticated(
                "Failed to authenticate user %s" % request.username
            )

        session = SessionStore()
        auth = {"username": request.username, "password": request.password}
        session["auth"] = auth
        session["_auth_user_id"] = u.pk
        session["_auth_user_backend"] = u.backend
        session.save()

        response = utility_pb2.LoginResponse()
        response.sessionid = session.session_key

        REQUEST_COUNT.labels("xos-core", "Utilities", "Login", grpc.StatusCode.OK).inc()
        return response

    @translate_exceptions("Utilities", "Logout")
    @track_request_time("Utilities", "Logout")
    def Logout(self, request, context):
        for (k, v) in context.invocation_metadata():
            if k.lower() == "x-xossession":
                s = SessionStore(session_key=v)
                if "_auth_user_id" in s:
                    del s["_auth_user_id"]
                    s.save()
        REQUEST_COUNT.labels("xos-core", "Utilities", "Login", grpc.StatusCode.OK).inc()
        return Empty()

    # FIXME are we still using these?
    @translate_exceptions("Utilities", "RunTosca")
    @track_request_time("Utilities", "RunTosca")
    def RunTosca(self, request, context):
        user = self.authenticate(context, required=True)

        sys_path_save = sys.path
        try:
            sys.path.append(toscadir)
            from tosca.engine import XOSTosca

            xt = XOSTosca(request.recipe, parent_dir=toscadir, log_to_console=False)
            xt.execute(user)
        except BaseException:
            response = utility_pb2.ToscaResponse()
            response.status = response.ERROR
            response.messages = traceback.format_exc()
            return response
        finally:
            sys.path = sys_path_save

        response = utility_pb2.ToscaResponse()
        response.status = response.SUCCESS
        response.messages = "\n".join(xt.log_msgs)

        return response

    @translate_exceptions("Utilities", "DestryTosca")
    @track_request_time("Utilities", "DestryTosca")
    def DestroyTosca(self, request, context):
        user = self.authenticate(context, required=True)

        sys_path_save = sys.path
        try:
            sys.path.append(toscadir)
            from tosca.engine import XOSTosca

            xt = XOSTosca(request.recipe, parent_dir=toscadir, log_to_console=False)
            xt.destroy(user)
        except BaseException:
            response = utility_pb2.ToscaResponse()
            response.status = response.ERROR
            response.messages = traceback.format_exc()
            return response
        finally:
            sys.path = sys_path_save

        response = utility_pb2.ToscaResponse()
        response.status = response.SUCCESS
        response.messages = "\n".join(xt.log_msgs)

        return response

    # end FIXME

    @translate_exceptions("Utilities", "NoOp")
    @track_request_time("Utilities", "NoOp")
    def NoOp(self, request, context):
        REQUEST_COUNT.labels("xos-core", "Utilities", "NoOp", grpc.StatusCode.OK).inc()
        return Empty()

    @translate_exceptions("Utilities", "AuthenticatedNoOp")
    @track_request_time("Utilities", "AuthenticatedNoOp")
    def AuthenticatedNoOp(self, request, context):
        self.authenticate(context, required=True)
        REQUEST_COUNT.labels(
            "xos-core", "Utilities", "AuthenticatedNoOp", grpc.StatusCode.OK
        ).inc()
        return Empty()

    @translate_exceptions("Utilities", "ListDirtyModels")
    @track_request_time("Utilities", "ListDirtyModels")
    def ListDirtyModels(self, request, context):
        dirty_models = utility_pb2.ModelList()

        models = django.apps.apps.get_models()
        for model in models:
            if is_internal_model(model):
                continue
            fieldNames = [x.name for x in model._meta.fields]
            if ("enacted" not in fieldNames) or ("updated" not in fieldNames):
                continue
            if (request.class_name) and (
                not fnmatch.fnmatch(model.__name__, request.class_name)
            ):
                continue
            objs = model.objects.filter(Q(enacted__lt=F("updated")) | Q(enacted=None))
            for obj in objs:
                item = dirty_models.items.add()
                item.class_name = model.__name__
                item.id = obj.id

        REQUEST_COUNT.labels(
            "xos-core", "Utilities", "ListDirtyModels", grpc.StatusCode.OK
        ).inc()
        return dirty_models

    @translate_exceptions("Utilities", "SetDirtyModels")
    @track_request_time("Utilities", "SetDirtyModels")
    def SetDirtyModels(self, request, context):
        user = self.authenticate(context, required=True)

        dirty_models = utility_pb2.ModelList()

        models = django.apps.apps.get_models()
        for model in models:
            if is_internal_model(model):
                continue
            fieldNames = [x.name for x in model._meta.fields]
            if ("enacted" not in fieldNames) or ("updated" not in fieldNames):
                continue
            if (request.class_name) and (
                not fnmatch.fnmatch(model.__name__, request.class_name)
            ):
                continue
            objs = model.objects.all()
            for obj in objs:
                try:
                    obj.caller = user
                    obj.save()
                    item = dirty_models.items.add()
                    item.class_name = model.__name__
                    item.id = obj.id
                except Exception as e:
                    item = dirty_models.items.add()
                    item.class_name = model.__name__
                    item.id = obj.id
                    item.info = str(e)

        REQUEST_COUNT.labels(
            "xos-core", "Utilities", "SetDirtyModels", grpc.StatusCode.OK
        ).inc()
        return dirty_models

    @translate_exceptions("Utilities", "GetXproto")
    @track_request_time("Utilities", "GetXproto")
    def GetXproto(self, request, context):
        res = utility_pb2.XProtos()

        core_dir = os.path.abspath(
            os.path.dirname(os.path.realpath(__file__)) + "/../core/models/"
        )
        core_xprotos = get_xproto(core_dir)

        service_dir = os.path.abspath(
            os.path.dirname(os.path.realpath(__file__)) + "/../services"
        )
        services_xprotos = get_xproto(service_dir)

        dynamic_service_dir = os.path.abspath(
            os.path.dirname(os.path.realpath(__file__)) + "/../dynamic_services"
        )
        dynamic_services_xprotos = get_xproto(dynamic_service_dir)

        xprotos = core_xprotos + services_xprotos + dynamic_services_xprotos

        xproto = ""

        for f in xprotos:
            content = open(f).read()
            xproto += "\n"
            xproto += content

        res.xproto = xproto
        REQUEST_COUNT.labels(
            "xos-core", "Utilities", "GetXproto", grpc.StatusCode.OK
        ).inc()
        return res

    @translate_exceptions("Utilities", "GetPopulatedServiceInstances")
    @track_request_time("Utilities", "GetPopulatedServiceInstances")
    def GetPopulatedServiceInstances(self, request, context):
        """
        Return a service instance with provider and subsciber service instance ids
        """
        response = utility_pb2.PopulatedServiceInstance()

        si = ServiceInstance.objects.get(id=request.id)

        # populate the response object
        response.id = si.id
        response.leaf_model_name = si.leaf_model_name
        response.owner_id = si.owner_id

        if si.name:
            response.name = si.name

        # find links
        provided_links = si.provided_links.all()
        subscribed_links = si.subscribed_links.all()

        # import pdb; pdb.set_trace()

        for l in provided_links:
            response.provided_service_instances.append(l.subscriber_service_instance.id)

        for l in subscribed_links:
            if l.subscriber_service_instance:
                response.subscribed_service_instances.append(
                    l.provider_service_instance_id
                )
            elif l.subscriber_service:
                response.subscribed_service.append(l.subscriber_service.id)
            elif l.subscriber_network:
                response.subscribed_network.append(l.subscriber_network.id)

        REQUEST_COUNT.labels(
            "xos-core", "Utilities", "GetPopulatedServiceInstances", grpc.StatusCode.OK
        ).inc()
        return response
