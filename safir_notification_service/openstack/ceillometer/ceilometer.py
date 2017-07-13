# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from ceilometerclient import client
from safir_notification_service.openstack.connector import OpenstackConnector

import threading

__ceilometerclient_version__ = '2'


def is_iterable(var):
    """Return True if the given is list or tuple.

    :param var: input object
    :return: True if var is list or tuple, else False
    """

    return (isinstance(var, (list, tuple)) or
            issubclass(var.__class__, (list, tuple)))


def make_query(user_id=None, tenant_id=None, resource_id=None,
               user_ids=None, tenant_ids=None, resource_ids=None):
    """Returns query built from given parameters.

    This query can be then used for querying resources, meters and
    statistics.

    :Parameters:
      - `user_id`: user_id, has a priority over list of ids
      - `tenant_id`: tenant_id, has a priority over list of ids
      - `resource_id`: resource_id, has a priority over list of ids
      - `user_ids`: list of user_ids
      - `tenant_ids`: list of tenant_ids
      - `resource_ids`: list of resource_ids
    """
    user_ids = user_ids or []
    tenant_ids = tenant_ids or []
    resource_ids = resource_ids or []

    query = []
    if user_id:
        user_ids = [user_id]
    for u_id in user_ids:
        query.append({"field": "user_id", "op": "eq", "value": u_id})

    if tenant_id:
        tenant_ids = [tenant_id]
    for t_id in tenant_ids:
        query.append({"field": "project_id", "op": "eq", "value": t_id})

    if resource_id:
        resource_ids = [resource_id]
    for r_id in resource_ids:
        query.append({"field": "resource_id", "op": "eq", "value": r_id})

    return query


class CeilometerClient:
    def __init__(self,
                 auth_username,
                 auth_password,
                 auth_url,
                 project_name,
                 user_domain_name,
                 project_domain_name):

        openstack_connector = OpenstackConnector(
            auth_username,
            auth_password,
            auth_url,
            project_name,
            user_domain_name,
            project_domain_name)
        session = openstack_connector.get_session()

        self.ceilometer_client = client.Client(__ceilometerclient_version__,
                                               session=session)

    def get_alarm(self, alarm_id):
        return self.ceilometer_client.alarms.get(alarm_id)

    def get_instance_id(self, alarm_id):
        alarm = self.get_alarm(alarm_id)
        return alarm.query['resource_id']

    def sample_list(self, meter_name, query=None, limit=None):
        """List the samples for this meters."""
        samples = self.ceilometer_client.samples.list(meter_name=meter_name,
                                                      q=query, limit=limit)
        return [Sample(s) for s in samples]

    def resource_list(self, query=None, ceilometer_usage_object=None):
        """List the resources."""
        resources = self.ceilometer_client.resources.list(q=query)
        return [Resource(r, ceilometer_usage_object) for r in resources]

    def statistic_list(self, meter_name, query=None, period=None):
        """List of statistics."""
        statistics = self.ceilometer_client.\
            statistics.list(meter_name=meter_name, q=query, period=period)
        return [Statistic(s) for s in statistics]

    def resources(self, query=None, filter_func=None,
                  with_users_and_tenants=False):
        """Obtaining resources with the query or filter_func.
        Obtains resources and also fetch tenants and users associated
        with those resources if with_users_and_tenants flag is true.
        :Parameters:
          - `query`: Query for fetching the Ceilometer Resources.
          - `filter_func`: Callable for filtering of the obtained
                           resources.
          - `with_users_and_tenants`: If true a user and a tenant object will
                                      be added to each resource object.
        """
        if with_users_and_tenants:
            ceilometer_usage_object = self
        else:
            ceilometer_usage_object = None
        resources = self.resource_list(
            query=query,
            ceilometer_usage_object=ceilometer_usage_object)
        if filter_func:
            resources = [resource for resource in resources if
                         filter_func(resource)]

        return resources

    def resources_with_statistics(self, query=None, meter_names=None,
                                  period=None, filter_func=None,
                                  stats_attr=None, additional_query=None,
                                  with_users_and_tenants=False):
        """Obtaining resources with statistics data inside.
        :Parameters:
          - `query`: Query for fetching the Ceilometer Resources.
          - `filter_func`: Callable for filtering of the obtained
                           resources.
          - `meter_names`: List of meter names of which we want the
                           statistics.
          - `period`: In seconds. If no period is given, only one aggregate
                      statistic is returned. If given, a faceted result will
                      be returned, divided into given periods. Periods with
                      no data are ignored.
          - `stats_attr`: String representing the specific name of the stats.
                          E.g. (avg, max, min...) If defined, meter attribute
                          will contain just the one value. If None is given,
                          meter attribute will contain the whole Statistic
                          object.
          - `additional_query`: Additional query for the statistics.
                                E.g. timespan, etc.
          - `with_users_and_tenants`: If true a user and a tenant object will
                                      be added to each resource object.
        """

        resources = self.resources(
            query, filter_func=filter_func,
            with_users_and_tenants=with_users_and_tenants)

        ThreadedUpdateResourceWithStatistics.process_list(
            self, resources,
            meter_names=meter_names, period=period, stats_attr=stats_attr,
            additional_query=additional_query)

        return resources

    def resource_aggregates(self, queries=None):
        """Obtaining resource aggregates with queries.
        Representing a resource aggregate by query is a most general way
        how to obtain a resource aggregates.
        :Parameters:
          - `queries`: Dictionary of named queries that defines a bulk of
                       resource aggregates.
        """
        resource_aggregates = []
        for identifier, query in queries.items():
            resource_aggregates.append(ResourceAggregate(query=query,
                                       ceilometer_usage=None,
                                       identifier=identifier))
        return resource_aggregates

    def resource_aggregates_with_statistics(self, queries=None,
                                            meter_names=None, period=None,
                                            filter_func=None, stats_attr=None,
                                            additional_query=None):
        """Obtaining resource aggregates with statistics data inside.
        :Parameters:
          - `queries`: Dictionary of named queries that defines a bulk of
                       resource aggregates.
          - `meter_names`: List of meter names of which we want the
                           statistics.
          - `period`: In seconds. If no period is given, only one aggregate
                      statistic is returned. If given, a faceted result will
                      be returned, divided into given periods. Periods with
                      no data are ignored.
          - `stats_attr`: String representing the specific name of the stats.
                          E.g. (avg, max, min...) If defined, meter attribute
                          will contain just the one value. If None is given,
                          meter attribute will contain the whole Statistic
                          object.
          - `additional_query`: Additional query for the statistics.
                                E.g. timespan, etc.
        """
        resource_aggregates = self.resource_aggregates(queries)

        ThreadedUpdateResourceWithStatistics.process_list(
            self,
            resource_aggregates, meter_names=meter_names, period=period,
            stats_attr=stats_attr, additional_query=additional_query)

        return resource_aggregates

    def update_with_statistics(self, resource, meter_names=None, period=None,
                               stats_attr=None, additional_query=None):
        """Adding statistical data into one Resource or ResourceAggregate.
        It adds each statistic of each meter_names into the resource
        attributes. Attribute name is the meter name with replaced '.' to '_'.
        :Parameters:
          - `resource`: Resource or ResourceAggregate object, that will
                        be filled by statistic data.
          - `meter_names`: List of meter names of which we want the
                           statistics.
          - `period`: In seconds. If no period is given, only one aggregate
                      statistic is returned. If given a faceted result will be
                      returned, dividend into given periods. Periods with no
                      data are ignored.
          - `stats_attr`: String representing the specific name of the stats.
                          E.g. (avg, max, min...) If defined, meter attribute
                          will contain just the one value. If None is given,
                          meter attribute will contain the whole Statistic
                          object.
          - `additional_query`: Additional query for the statistics.
                                E.g. timespan, etc.
        """

        if not meter_names:
            raise ValueError("meter_names and resources must be defined to be "
                             "able to obtain the statistics.")

        # query for identifying one resource in meters
        query = resource.query
        if additional_query:
            if not is_iterable(additional_query):
                raise ValueError("Additional query must be list of"
                                 " conditions. See the docs for format.")
            query = query + additional_query

        for meter in meter_names:
            statistics = self.statistic_list(meter,
                                             query=query,
                                             period=period)
            meter = meter.replace(".", "_")
            if statistics:
                if stats_attr:
                    # I want to load only a specific attribute
                    resource.set_meter(
                        meter,
                        getattr(statistics[0], stats_attr, None))
                else:
                    # I want a dictionary of all statistics
                    resource.set_meter(meter, statistics)
            else:
                resource.set_meter(meter, None)

        return resource


class APIResourceWrapper(object):
    """Simple wrapper for api objects.
    Define _attrs on the child class and pass in the
    api object as the only argument to the constructor
    """
    _attrs = []
    _apiresource = None  # Make sure _apiresource is there even in __init__.

    def __init__(self, apiresource):
        self._apiresource = apiresource

    def __getattribute__(self, attr):
        try:
            return object.__getattribute__(self, attr)
        except AttributeError:
            if attr not in self._attrs:
                raise
            # __getattr__ won't find properties
            return getattr(self._apiresource, attr)

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__,
                             dict((attr, getattr(self, attr))
                                  for attr in self._attrs
                                  if hasattr(self, attr)))

    def to_dict(self):
        obj = {}
        for key in self._attrs:
            obj[key] = getattr(self._apiresource, key, None)
        return obj


class Sample(APIResourceWrapper):
    """Represents one Ceilometer sample."""

    _attrs = ['counter_name', 'user_id', 'resource_id', 'timestamp',
              'resource_metadata', 'source', 'counter_unit', 'counter_volume',
              'project_id', 'counter_type', 'resource_metadata']

    @property
    def instance(self):
        display_name = self.resource_metadata.get('display_name', None)
        instance_id = self.resource_metadata.get('instance_id', None)
        return display_name or instance_id

    @property
    def name(self):
        name = self.resource_metadata.get("name", None)
        display_name = self.resource_metadata.get("display_name", None)
        return name or display_name or ""


class Resource(APIResourceWrapper):
    """Represents one Ceilometer resource."""
    _attrs = ['resource_id', 'source', 'user_id', 'project_id', 'metadata',
              'links']

    def __init__(self, apiresource, ceilometer_usage=None):
        super(Resource, self).__init__(apiresource)

        # Save empty strings to IDs rather than None, so it gets
        # serialized correctly. We don't want 'None' strings.
        self.project_id = self.project_id or ""
        self.user_id = self.user_id or ""
        self.resource_id = self.resource_id or ""

        self._id = "%s__%s__%s" % (self.project_id,
                                   self.user_id,
                                   self.resource_id)

        # Meters with statistics data
        self._meters = {}

        if ceilometer_usage and self.project_id:
            self._tenant = ceilometer_usage.get_tenant(self.project_id)
        else:
            self._tenant = None

        if ceilometer_usage and self.user_id:
            self._user = ceilometer_usage.get_user(self.user_id)
        else:
            self._user = None

        self._query = make_query(tenant_id=self.project_id,
                                 user_id=self.user_id,
                                 resource_id=self.resource_id)

    @property
    def name(self):
        name = self.metadata.get("name", None)
        display_name = self.metadata.get("display_name", None)
        return name or display_name or ""

    @property
    def id(self):
        return self._id

    @property
    def tenant(self):
        return self._tenant

    @property
    def user(self):
        return self._user

    @property
    def resource(self):
        return self.resource_id

    @property
    def query(self):
        return self._query

    @property
    def meters(self):
        return self._meters

    def get_meter(self, meter_name):
        return self._meters.get(meter_name, None)

    def set_meter(self, meter_name, value):
        self._meters[meter_name] = value


class Statistic(APIResourceWrapper):
    """Represents one Ceilometer statistic."""

    _attrs = ['period', 'period_start', 'period_end',
              'count', 'min', 'max', 'sum', 'avg',
              'duration', 'duration_start', 'duration_end']


class ResourceAggregate(Resource):
    """Represents aggregate of more resources together.
    Aggregate of resources can be obtained by specifying
    multiple ids in one parameter or by not specifying
    one parameter.
    It can also be specified by query directly.
    Example:
        We can obtain an aggregate of resources by specifying
        multiple resource_ids in resource_id parameter in init.
        Or we can specify only tenant_id, which will return
        all resources of that tenant.
    """

    def __init__(self, tenant_id=None, user_id=None, resource_id=None,
                 tenant_ids=None, user_ids=None, resource_ids=None,
                 ceilometer_usage=None, query=None, identifier=None):

        self._id = identifier

        self.tenant_id = None
        self.user_id = None
        self.resource_id = None

        # Meters with statistics data
        self._meters = {}

        if query:
            self._query = query
        else:
            if ceilometer_usage and tenant_id:
                self.tenant_id = tenant_id
                self._tenant = ceilometer_usage.get_tenant(tenant_id)
            else:
                self._tenant = None

            if ceilometer_usage and user_id:
                self.user_id = user_id
                self._user = ceilometer_usage.get_user(user_id)
            else:
                self._user = None

            if resource_id:
                self.resource_id = resource_id

            self._query = make_query(tenant_id=tenant_id, user_id=user_id,
                                     resource_id=resource_id,
                                     tenant_ids=tenant_ids,
                                     user_ids=user_ids,
                                     resource_ids=resource_ids)

    @property
    def id(self):
        return self._id


class ThreadedUpdateResourceWithStatistics(threading.Thread):
    """Multithread wrapper for update_with_statistics method of
    resource_usage.
    A join logic is placed in process_list class method. All resources
    will have its statistics attribute filled in separate threads.
    The resource_usage object is shared between threads. Each thread is
    updating one Resource.
    :Parameters:
      - `resource`: Resource or ResourceAggregate object, that will
                    be filled by statistic data.
      - `resources`: List of Resource or ResourceAggregate object,
                     that will be filled by statistic data.
      - `resource_usage`: Wrapping resource usage object, that holds
                          all statistics data.
      - `meter_names`: List of meter names of the statistics we want.
      - `period`: In seconds. If no period is given, only one aggregate
                  statistic is returned. If given, a faceted result will be
                  returned, divided into given periods. Periods with no
                  data are ignored.
      - `stats_attr`: String representing the attribute name of the stats.
                      E.g. (avg, max, min...) If None is given, whole
                      statistic object is returned,
      - `additional_query`: Additional query for the statistics.
                            E.g. timespan, etc.
    """

    def __init__(self, resource_usage, resource, meter_names=None,
                 period=None, filter_func=None, stats_attr=None,
                 additional_query=None):
        super(ThreadedUpdateResourceWithStatistics, self).__init__()
        self.resource_usage = resource_usage
        self.resource = resource
        self.meter_names = meter_names
        self.period = period
        self.stats_attr = stats_attr
        self.additional_query = additional_query

    def run(self):
        # Run the job
        self.resource_usage.update_with_statistics(
            self.resource,
            meter_names=self.meter_names, period=self.period,
            stats_attr=self.stats_attr, additional_query=self.additional_query)

    @classmethod
    def process_list(cls, resource_usage, resources, meter_names=None,
                     period=None, filter_func=None, stats_attr=None,
                     additional_query=None):
        threads = []

        for resource in resources:
            # add statistics data into resource
            thread = cls(resource_usage, resource, meter_names=meter_names,
                         period=period, stats_attr=stats_attr,
                         additional_query=additional_query)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()
