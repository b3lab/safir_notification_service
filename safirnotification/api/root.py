# -*- coding: utf-8 -*-
# Copyright 2017 TUBITAK B3LAB
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo_config import cfg
import pecan
from pecan import rest
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan

from safirnotification.api.v1 import controllers as v1_api

CONF = cfg.CONF
CONF.import_opt('port', 'safirnotification.api.app', 'api')


class APILink(wtypes.Base):

    type = wtypes.text
    """Type of link."""

    rel = wtypes.text
    """Relationship with this link."""

    href = wtypes.text
    """URL of the link."""

    @classmethod
    def sample(cls):
        version = 'v1'
        sample = cls(
            rel='self',
            type='text/html',
            href='http://127.0.0.1:{port}/{id}'.format(
                port=CONF.api.port,
                id=version))
        return sample


class APIMediaType(wtypes.Base):

    base = wtypes.text
    """Base type of this media type."""

    type = wtypes.text
    """Type of this media type."""

    @classmethod
    def sample(cls):
        sample = cls(
            base='application/json',
            type='application/vnd.openstack.safirnotification-v1+json')
        return sample


VERSION_STATUS = wtypes.Enum(wtypes.text, 'EXPERIMENTAL', 'STABLE')


class APIVersion(wtypes.Base):

    id = wtypes.text
    """ID of the version."""

    status = VERSION_STATUS
    """Status of the version."""

    updated = wtypes.text
    "Last update in iso8601 format."

    links = [APILink]
    """List of links to API resources."""

    media_types = [APIMediaType]
    """Types accepted by this API."""

    @classmethod
    def sample(cls):
        version = 'v1'
        updated = '2017-10-26T11:46:00Z'
        links = [APILink.sample()]
        media_types = [APIMediaType.sample()]
        sample = cls(id=version,
                     status='STABLE',
                     updated=updated,
                     links=links,
                     media_types=media_types)
        return sample


class RootController(rest.RestController):

    v1 = v1_api.V1Controller()

    @wsme_pecan.wsexpose([APIVersion])
    def index(self):
        ver1 = APIVersion(
            id='v1',
            status='EXPERIMENTAL',
            updated='2017-10-26T11:46:00Z',
            links=[
                APILink(
                    rel='self',
                    href='{scheme}://{host}/v1'.format(
                        scheme=pecan.request.scheme,
                        host=pecan.request.host,
                    )
                )
            ],
            media_types=[]
        )

        versions = []
        versions.append(ver1)

        return versions
