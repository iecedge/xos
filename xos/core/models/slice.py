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
from slice_decl import *


class Slice(Slice_decl):
    class Meta:
        proxy = True

    NETWORK_CHOICES = (
        (None, "Default"),
        ("host", "Host"),
        ("bridged", "Bridged"),
        ("noauto", "No Automatic Networks"),
    )

    def save(self, *args, **kwargs):
        # set creator on first save
        if not self.creator and hasattr(self, "caller"):
            self.creator = self.caller

        # TODO: Verify this logic is still in use
        # only admins change a slice's creator
        if "creator" in self.changed_fields and (
            not hasattr(self, "caller") or not self.caller.is_admin
        ):

            if (self._initial["creator"] is None) and (
                self.creator == getattr(self, "caller", None)
            ):
                # it's okay if the creator is being set by the caller to
                # himeself on a new slice object.
                pass
            else:
                raise PermissionDenied(
                    "Insufficient privileges to change slice creator",
                    {"creator": "Insufficient privileges to change slice creator"},
                )

        if self.network == "Private Only":
            # "Private Only" was the default from the old Tenant View
            self.network = None
        self.enforce_choices(self.network, self.NETWORK_CHOICES)

        super(Slice, self).save(*args, **kwargs)
