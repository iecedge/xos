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

# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-03-20 23:53
from __future__ import unicode_literals

import core.models.xosbase_header
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0009_auto_20190313_1442'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestserviceDuplicateServiceInstance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, help_text=b'Time this model was created')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, help_text=b'Time this model was changed by a non-synchronizer')),
                ('enacted', models.DateTimeField(blank=True, default=None, help_text=b'When synced, set to the timestamp of the data that was synced', null=True)),
                ('policed', models.DateTimeField(blank=True, default=None, help_text=b'When policed, set to the timestamp of the data that was policed', null=True)),
                ('backend_register', models.CharField(blank=True, default=b'{}', max_length=1024, null=True)),
                ('backend_need_delete', models.BooleanField(default=False)),
                ('backend_need_reap', models.BooleanField(default=False)),
                ('backend_status', models.CharField(default=b'Provisioning in progress', max_length=1024)),
                ('backend_code', models.IntegerField(default=0)),
                ('deleted', models.BooleanField(default=False)),
                ('write_protect', models.BooleanField(default=False)),
                ('lazy_blocked', models.BooleanField(default=False)),
                ('no_sync', models.BooleanField(default=False)),
                ('no_policy', models.BooleanField(default=False)),
                ('policy_status', models.CharField(blank=True, default=b'Policy in process', max_length=1024, null=True)),
                ('policy_code', models.IntegerField(blank=True, default=0, null=True)),
                ('leaf_model_name', models.CharField(help_text=b'The most specialized model in this chain of inheritance, often defined by a service developer', max_length=1024)),
                ('backend_need_delete_policy', models.BooleanField(default=False, help_text=b'True if delete model_policy must be run before object can be reaped')),
                ('xos_managed', models.BooleanField(default=True, help_text=b'True if xos is responsible for creating/deleting this object')),
                ('backend_handle', models.CharField(blank=True, help_text=b'Handle used by the backend to track this object', max_length=1024, null=True)),
                ('changed_by_step', models.DateTimeField(blank=True, default=None, help_text=b'Time this model was changed by a sync step', null=True)),
                ('changed_by_policy', models.DateTimeField(blank=True, default=None, help_text=b'Time this model was changed by a model policy', null=True)),
                ('name', models.CharField(help_text=b'Named copied From serviceInstance', max_length=256)),
                ('some_integer', models.IntegerField(default=0)),
                ('some_other_integer', models.IntegerField(default=0)),
                ('optional_string', models.TextField(blank=True, null=True)),
                ('optional_string_with_default', models.TextField(blank=True, default=b'some_default', null=True)),
                ('optional_string_with_choices', models.TextField(blank=True, choices=[(b'one', b'one'), (b'two', b'two')], null=True)),
                ('optional_string_max_length', models.CharField(blank=True, max_length=32, null=True)),
                ('optional_string_stripped', core.models.xosbase_header.StrippedCharField(blank=True, max_length=32, null=True)),
                ('optional_string_date', models.DateTimeField(blank=True, null=True)),
                ('optional_string_ip', models.GenericIPAddressField(blank=True, null=True)),
                ('optional_string_indexed', models.TextField(blank=True, db_index=True, null=True)),
                ('required_string', models.TextField(default=b'some_default')),
                ('required_bool_default_false', models.BooleanField(default=False)),
                ('required_bool_default_true', models.BooleanField(default=True)),
                ('optional_int', models.IntegerField(blank=True, null=True)),
                ('optional_int_with_default', models.IntegerField(blank=True, default=123, null=True)),
                ('optional_int_with_min', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(100)])),
                ('optional_int_with_max', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(199)])),
                ('required_int_with_default', models.IntegerField(default=456)),
                ('optional_float', models.FloatField(blank=True, null=True)),
                ('optional_float_with_default', models.FloatField(blank=True, default=3.3, null=True)),
            ],
            options={
                'verbose_name': 'Testservice Duplicate Service Instance',
            },
            bases=(models.Model, core.models.xosbase_header.PlModelMixIn),
        ),
        migrations.CreateModel(
            name='TestserviceService',
            fields=[
                ('service_decl_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.Service_decl')),
            ],
            options={
                'verbose_name': 'Testservice Service',
            },
            bases=('core.service',),
        ),
        migrations.CreateModel(
            name='TestserviceServiceInstance',
            fields=[
                ('serviceinstance_decl_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.ServiceInstance_decl')),
                ('sync_after_policy', models.BooleanField(default=False)),
                ('sync_during_policy', models.BooleanField(default=False)),
                ('policy_after_sync', models.BooleanField(default=False)),
                ('policy_during_sync', models.BooleanField(default=False)),
                ('update_during_sync', models.BooleanField(default=False)),
                ('update_during_policy', models.BooleanField(default=False)),
                ('create_duplicate', models.BooleanField(default=False)),
                ('some_integer', models.IntegerField(default=0)),
                ('some_other_integer', models.IntegerField(default=0)),
                ('optional_string', models.TextField(blank=True, null=True)),
                ('optional_string_with_default', models.TextField(blank=True, default=b'some_default', null=True)),
                ('optional_string_with_choices', models.TextField(blank=True, choices=[(b'one', b'one'), (b'two', b'two')], null=True)),
                ('optional_string_max_length', models.CharField(blank=True, max_length=32, null=True)),
                ('optional_string_stripped', core.models.xosbase_header.StrippedCharField(blank=True, max_length=32, null=True)),
                ('optional_string_date', models.DateTimeField(blank=True, null=True)),
                ('optional_string_ip', models.GenericIPAddressField(blank=True, null=True)),
                ('optional_string_indexed', models.TextField(blank=True, db_index=True, null=True)),
                ('required_string', models.TextField(default=b'some_default')),
                ('required_bool_default_false', models.BooleanField(default=False)),
                ('required_bool_default_true', models.BooleanField(default=True)),
                ('optional_int', models.IntegerField(blank=True, null=True)),
                ('optional_int_with_default', models.IntegerField(blank=True, default=123, null=True)),
                ('optional_int_with_min', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(100)])),
                ('optional_int_with_max', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(199)])),
                ('required_int_with_default', models.IntegerField(default=456)),
                ('optional_float', models.FloatField(blank=True, null=True)),
                ('optional_float_with_default', models.FloatField(blank=True, default=3.3, null=True)),
            ],
            options={
                'verbose_name': 'Testservice Service Instance',
            },
            bases=('core.serviceinstance',),
        ),
        migrations.AddField(
            model_name='testserviceduplicateserviceinstance',
            name='serviceinstance',
            field=models.ForeignKey(help_text=b'Link to the ServiceInstance this was duplicated from', on_delete=django.db.models.deletion.CASCADE, related_name='duplicates', to='testservice.TestserviceServiceInstance'),
        ),
    ]
