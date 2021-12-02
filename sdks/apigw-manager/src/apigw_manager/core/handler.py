# -*- coding: utf-8 -*-
"""
 * TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-蓝鲸 PaaS 平台(BlueKing-PaaS) available.
 * Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at http://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
"""
import json
import logging
import typing

from bkapi.bk_apigateway.client import Client as BKAPIGatewayClient
from future.utils import raise_from

from apigw_manager.core.exceptions import ApiException, ApiResultError

if typing.TYPE_CHECKING:
    from apigw_manager.core import configuration

logger = logging.getLogger(__name__)


class Handler(object):
    def __init__(self, config):
        self.config = config  # type: configuration.Configuration

        self.client = BKAPIGatewayClient(endpoint=config.host, stage=config.stage)

    def __post_init__(self):
        pass

    def _get_bkapi_authorization(self):
        """Get authentication information"""
        return json.dumps(
            {
                "bk_app_code": self.config.bk_app_code,
                "bk_app_secret": self.config.bk_app_secret,
                "access_token": self.config.access_token,
            }
        )

    def _get_from_cache(self, operation_id, data):
        api_cache = self.config.api_cache
        if not api_cache:
            return False, None

        return api_cache.try_get(operation_id, data)

    def _put_into_cache(self, operation_id, data, result):
        api_cache = self.config.api_cache
        if api_cache:
            api_cache.update(operation_id, data, result)
            return True

        return False

    def _call_with_cache(self, operation_id, **kwargs):
        """Call the API instance, allow data to be retrieved from the cache"""
        cache_key = {
            "api_name": kwargs.get("api_name", self.config.api_name),
            "kwargs": kwargs,
        }

        cached, result = self._get_from_cache(operation_id, cache_key)
        if cached:
            return result

        result = self._call(operation_id, **kwargs)

        self._put_into_cache(operation_id, cache_key, result)

        return result

    def _call(self, operation_id, files=None, **kwargs):
        """Call the API instance"""
        data = {
            "path_params": {"api_name": kwargs.pop("api_name", self.config.api_name)},
            "data": kwargs,
            "headers": {
                "X-Bkapi-Authorization": kwargs.pop("x_bkapi_authorization", self._get_bkapi_authorization()),
            },
            "files": files,
        }

        logger.debug("call api %s, data: %s", operation_id, data)

        try:
            return getattr(self.client.api, operation_id)(**data)
        except Exception as err:
            raise_from(ApiException(operation_id), err)

    def _parse_result(self, result, convertor, code=0):
        """Check the code and convert the result"""
        logger.debug("code %s, message: %s", result.get("code"), result.get("message"))
        if result.get("code") != code:
            raise ApiResultError(
                result.get("code"),
                result.get("message"),
            )

        return convertor(result)