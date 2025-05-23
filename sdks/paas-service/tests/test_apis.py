# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making
蓝鲸智云 - PaaS 平台 (BlueKing - PaaS System) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except
in compliance with the License. You may obtain a copy of the License at

    http://opensource.org/licenses/MIT

Unless required by applicable law or agreed to in writing, software distributed under
the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied. See the License for the specific language governing permissions and
limitations under the License.

We undertake not to change the open source license (MIT license) applicable
to the current version of the project delivered to anyone in the future.
"""
import json

import pytest
from paas_service.constants import DEFAULT_TENANT_ID
from paas_service.models import Plan, Service, ServiceInstanceConfig, SpecDefinition, Specification
from paas_service.views import PlanManageViewSet, ServiceManageViewSet, SvcInstanceConfigViewSet, SvcInstanceViewSet

pytestmark = pytest.mark.django_db
spec_def_data = {
    "name": "foo",
    # SpecDefinition 表中只有 display_name 字段需要国际化
    "display_name_zh_cn": "简介",
    "display_name_en": "FOO",
    "description": "this is foo.",
    "recommended_value": "Foo",
}


class TestInstanceConfigUpdate:
    """Test cases for InstanceConfig update view"""

    def test_update_normal(self, rf, instance, platform_client):
        view = SvcInstanceConfigViewSet.as_view({'put': 'update'})

        request = rf.put(
            f'/{instance.pk}/',
            json.dumps(
                {'paas_app_info': {'app_id': 'foo', 'app_name': 'foo-应用', 'module': 'backend', 'environment': 'stag'}}
            ),
            content_type='application/json',
        )
        request.client = platform_client

        response = view(request, instance_id=instance.pk)
        response.render()
        assert response.status_code == 200
        assert response.data['paas_app_info']['app_id'] == 'foo'
        assert response.data['tenant_id'] == DEFAULT_TENANT_ID


class TestInstanceConfigRetrieve:
    def test_retrieve_not_initialized(self, rf, instance, platform_client):
        view = SvcInstanceConfigViewSet.as_view({'get': 'retrieve'})

        request = rf.get(
            f'/{instance.pk}/',
        )
        request.client = platform_client

        response = view(request, instance_id=instance.pk)
        response.render()
        assert response.status_code == 400

    def test_retrieve_normal(self, rf, instance, platform_client):
        view = SvcInstanceConfigViewSet.as_view({'get': 'retrieve'})

        request = rf.get(
            f'/{instance.pk}/',
        )
        request.client = platform_client

        config, _ = ServiceInstanceConfig.objects.update_or_create(
            instance=instance, tenant_id=instance.tenant_id, defaults={'paas_app_info': {'app_id': 'foo'}}
        )
        response = view(request, instance_id=instance.pk)
        response.render()
        assert response.status_code == 200
        assert response.data['paas_app_info']['app_id'] == 'foo'
        assert response.data['tenant_id'] == DEFAULT_TENANT_ID


class TestServiceManageViewSet:
    def test_list(self, rf, service, plan, platform_client):
        view = ServiceManageViewSet.as_view({'get': 'list'})

        request = rf.get("/services/")
        request.client = platform_client

        response = view(request)
        response.render()

        assert len(response.data) == 1
        service_data = response.data[0]
        assert service_data["uuid"] == str(service.uuid)

        assert len(service_data["plans"]) == 1
        plan_data = service_data["plans"][0]
        assert plan_data["uuid"] == str(plan.uuid)
        assert plan_data["tenant_id"] == DEFAULT_TENANT_ID

    @pytest.mark.parametrize(
        "service_data",
        [
            {"name": "Service", "specifications": [spec_def_data]},
            {
                "name": "Service",
                "category": 1,
                "display_name_zh_cn": "增强服务",
                "description_zh_cn": "简介文案",
                "long_description_zh_cn": "描述文案" * 1024,
                "config": {"foo": "bar"},
                "specifications": [spec_def_data],
            },
            {
                'name': 'redis',
                'category': 1,
                'display_name_zh_cn': 'Redis',
                'logo': 'data:image/png;base64,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',  # noqa
                'description_zh_cn': 'redis',
                'long_description_zh_cn': 'redis',
                'instance_tutorial_zh_cn': "通过环境变量来获取对应的值：\n\n```\nREDIS_HOST = os.environ.get('REDIS_HOST')\nREDIS_PORT = int(os.environ.get('REDIS_PORT'))\nREDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')\n```\n\n蓝鲸 Python 开发框架默认使用 RabbitMQ 作为 Celery 的 BROKER_URL；如需使用 Redis，请在 Django 的配置中手动设置 BROKER_URL 的值:\n\n```\nBROKER_URL = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/0'\n```",  # noqa
                'available_languages': 'python',
                'config': {},
                'is_active': True,
                'is_visible': True,
                'specifications': [spec_def_data],
            },
        ],
    )
    def test_update(self, rf, service, platform_client, service_data):
        view = ServiceManageViewSet.as_view({'put': 'update'})
        request = rf.put(
            f"/services/{service.uuid}/",
            data=json.dumps(service_data),
            content_type="application/json",
        )
        request.client = platform_client

        response = view(request, service_id=service.uuid)
        response.render()

        assert response.status_code == 204
        assert Service.objects.count() == 1
        assert SpecDefinition.objects.count() == 1

        service.refresh_from_db()
        for k, v in service_data.items():
            if k != "specifications":
                assert getattr(service, k) == v

        definition = service.specifications.get(name="foo")
        for k, v in spec_def_data.items():
            assert getattr(definition, k) == v

    def test_create(self, rf, platform_client):
        view = ServiceManageViewSet.as_view({'post': 'create'})
        spec_def_data = {
            "name": "foo",
            "display_name_en": "FOO",
            "display_name_zh_cn": "FOO",
            # "description": "this is foo.",
            "recommended_value": "Foo",
        }
        service_data = {
            "name": "Service",
            "category": 1,
            "display_name_en": "add ons",
            "display_name_zh_cn": "增强服务",
            "description_zh_cn": "简介文案",
            "long_description_zh_cn": "描述文案" * 1024,
            "config": {"foo": "bar"},
            "specifications": [spec_def_data],
        }

        request = rf.post(
            "/services/",
            data=json.dumps(service_data),
            content_type="application/json",
        )
        request.client = platform_client

        response = view(request)
        response.render()

        assert response.status_code == 201
        assert Service.objects.count() == 1
        assert SpecDefinition.objects.count() == 1

        service = Service.objects.get()
        for k, v in service_data.items():
            if k != "specifications":
                assert getattr(service, k) == v

        definition = service.specifications.get(name="foo")
        for k, v in spec_def_data.items():
            assert getattr(definition, k) == v


class TestPlanManageViewSet:
    @pytest.mark.parametrize(
        "plan_data",
        [
            {"name": "Plan", "specifications": {"foo": "Bar"}},
            {"name": "Plan", "specifications": {"foo": "Bar"}, "properties": {}},
            {"name": "Plan", "specifications": {"foo": "Bar"}, "properties": {}, "tenant_id": "tenant_id_x"},
        ],
    )
    def test_update(self, rf, service, spec_def, plan, platform_client, plan_data):
        view = PlanManageViewSet.as_view({'put': 'update'})
        request = rf.put(
            f"/plans/{plan.uuid}/",
            data=json.dumps(plan_data),
            content_type="application/json",
        )
        request.client = platform_client

        response = view(request, plan_id=plan.uuid)
        response.render()
        assert response.status_code == 204
        assert Plan.objects.count() == 1
        assert Specification.objects.count() == 1

        plan.refresh_from_db()
        plan = Plan.objects.get()
        for k, v in plan_data.items():
            if k == "service":
                getattr(plan, k) == service
            elif k != "specifications":
                assert getattr(plan, k) == v

        spec = plan.specifications.get(definition=spec_def)
        assert spec.value == "Bar"

    def test_create(self, rf, service, spec_def, platform_client):
        plan_data = {
            "name": "Plan",
            "specifications": {"foo": "Bar"},
            "properties": {},
            "service": str(service.uuid),
            "region": "r1",
            "tenant_id": "tenant_id_x",
        }

        view = PlanManageViewSet.as_view({'post': 'create'})
        request = rf.post(
            "/plans/",
            data=json.dumps(plan_data),
            content_type="application/json",
        )
        request.client = platform_client

        response = view(request)
        response.render()

        assert response.status_code == 201
        assert Plan.objects.count() == 1
        assert SpecDefinition.objects.count() == 1

        plan = Plan.objects.get()
        for k, v in plan_data.items():
            if k == "service":
                getattr(plan, k) == service
            elif k == "properties":
                assert getattr(plan, k) != v
                assert getattr(plan, k) == {"region": "r1"}
            elif k not in ["specifications", "region"]:
                assert getattr(plan, k) == v

        spec = plan.specifications.get(definition=spec_def)
        assert spec.value == "Bar"


class TestSvcInstanceViewSet:
    def test_retrieve_by_fields(self, rf, service, instance_with_credentials, platform_client):
        name = instance_with_credentials.get_credentials().get('name')
        view = SvcInstanceViewSet.as_view({'get': 'retrieve_by_fields'})

        request = rf.get(
            f'/{service.pk}/?name={name}',
        )
        request.client = platform_client

        response = view(request, service_id=service.pk)
        response.render()
        assert response.status_code == 200
        assert response.data['uuid'] == str(instance_with_credentials.uuid)
        assert response.data['tenant_id'] == DEFAULT_TENANT_ID

    def test_retrieve_by_fields_when_not_found(self, rf, service, platform_client):
        name = 'test'
        view = SvcInstanceViewSet.as_view({'get': 'retrieve_by_fields'})

        request = rf.get(
            f'/{service.pk}/?name={name}',
        )
        request.client = platform_client

        response = view(request, service_id=service.pk)
        response.render()
        assert response.status_code == 404

    def test_retrieve(self, rf, service, instance_with_credentials, platform_client):
        view = SvcInstanceViewSet.as_view({'get': 'retrieve'})

        request = rf.get(f"/instances/{instance_with_credentials.pk}")
        request.client = platform_client

        response = view(request, instance_id=instance_with_credentials.pk)
        response.render()
        assert response.status_code == 200
        assert response.data["uuid"] == str(instance_with_credentials.uuid)

    def test_retrieve_to_be_deleted(self, rf, service, instance_with_credentials, platform_client):
        instance_with_credentials.to_be_deleted = True
        instance_with_credentials.save()

        view = SvcInstanceViewSet.as_view({'get': 'retrieve'})

        request = rf.get(f"/instances/{instance_with_credentials.pk}/?to_be_deleted=true")
        request.client = platform_client

        response = view(request, instance_id=instance_with_credentials.pk)
        response.render()
        assert response.status_code == 200
        assert response.data["uuid"] == str(instance_with_credentials.uuid)
        assert response.data['tenant_id'] == DEFAULT_TENANT_ID

    def test_retrieve_when_not_found(self, rf, service, instance_with_credentials, platform_client):
        instance_with_credentials.to_be_deleted = True
        instance_with_credentials.save()

        view = SvcInstanceViewSet.as_view({'get': 'retrieve'})

        request = rf.get(f"/instances/{instance_with_credentials.pk}")
        request.client = platform_client

        response = view(request, instance_id=instance_with_credentials.pk)
        response.render()
        assert response.status_code == 404

    def test_retrieve_to_be_deleted_when_not_found(self, rf, service, instance_with_credentials, platform_client):
        view = SvcInstanceViewSet.as_view({'get': 'retrieve'})

        request = rf.get(f"/instances/{instance_with_credentials.pk}/?to_be_deleted=true")
        request.client = platform_client

        response = view(request, instance_id=instance_with_credentials.pk)
        response.render()
        assert response.status_code == 404
