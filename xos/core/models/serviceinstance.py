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

from django.db.models.fields import NOT_PROVIDED
from xos.exceptions import XOSValidationError, XOSMissingField, XOSDuplicateKey
from serviceinstance_decl import *


class ServiceInstance(ServiceInstance_decl):
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super(ServiceInstance, self).__init__(*args, **kwargs)

    # TODO: Used by CordSubscriberRoot. Verify whether the usage is necessary.
    def validate_unique_service_specific_id(self, none_okay=False):
        if not none_okay and (self.service_specific_id is None):
            raise XOSMissingField(
                "subscriber_specific_id is None, and it's a required field",
                fields={"service_specific_id": "cannot be none"},
            )

        if self.service_specific_id:
            conflicts = self.__class__.objects.filter(
                service_specific_id=self.service_specific_id
            )
            if self.pk:
                conflicts = conflicts.exclude(pk=self.pk)
            if conflicts:
                raise XOSDuplicateKey(
                    "service_specific_id %s already exists" % self.service_specific_id,
                    fields={"service_specific_id": "duplicate key"},
                )

    def set_owner(self):
        if hasattr(self, "OWNER_CLASS_NAME"):
            owner_class = self.get_model_class_by_name(self.OWNER_CLASS_NAME)
            if not owner_class:
                raise XOSValidationError(
                    "Cannot find owner class %s" % self.OWNER_CLASS_NAME
                )

            need_set_owner = True
            if self.owner_id:
                # Check to see if owner is set to a valid instance of owner_class. If it is, then we already have an
                # owner. If it is not, then some other misbehaving class must have altered the ServiceInstance.meta
                # to point to its own default (these services are being cleaned up).
                if owner_class.objects.filter(id=self.owner_id).exists():
                    need_set_owner = False

            if need_set_owner:
                owners = owner_class.objects.all()
                if not owners:
                    raise XOSValidationError(
                        "Cannot find eligible owner of class %s" % self.OWNER_CLASS_NAME
                    )

                self.owner = owners[0]
        else:
            # Deal with legacy services that specify their owner as _meta field default. This is a workaround for
            # what is probably a django bug (if a SerivceInstance without a default is created before a ServiceInstance
            # that does have a default, then the later service's default is not honored by django).

            # TODO: Delete this after all services have been migrated away from using field defaults

            if (
                (not self.owner_id)
                and (self._meta.get_field("owner").default)
                and (self._meta.get_field("owner").default != NOT_PROVIDED)
            ):
                self.owner = Service.objects.get(
                    id=self._meta.get_field("owner").default
                )

    def full_clean(self, *args, **kwargs):
        # NOTE: SEBA-222 Must be called before full_clean, otherwise a non-null violation will occur if the
        # owner is None.
        if not self.deleted:
            self.set_owner()

        super(ServiceInstance,self).full_clean()

    def save(self, *args, **kwargs):
        # If the model has a Creator and it's not specified, then attempt to default to the Caller. Caller is
        # automatically filled in my the API layer. This code was typically used by ServiceInstances that lead to
        # instance creation.
        if (
            (hasattr(self, "creator"))
            and (not self.creator)
            and (hasattr(self, "caller"))
            and (self.caller)
        ):
            self.creator = self.caller

        super(ServiceInstance, self).save(*args, **kwargs)
