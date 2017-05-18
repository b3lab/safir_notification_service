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

import datetime
import pytz


def calc_date_args(date_from, date_to):
    try:
        if date_from:
            date_from = pytz.utc.localize(
                datetime.datetime.strptime(str(date_from), "%Y-%m-%d"))
        else:
            pass
        if date_to:
            date_to = pytz.utc.localize(
                datetime.datetime.strptime(str(date_to), "%Y-%m-%d"))
            # It returns the beginning of the day, I want the end of
            # the day, so I add one day without a second.
            date_to = (date_to + datetime.timedelta(days=1) -
                       datetime.timedelta(seconds=1))
        else:
            date_to = datetime.time.now()
    except Exception:
        raise ValueError("The dates haven't been recognized")
    return date_from, date_to


def series_for_meter(aggregates, group_by, meter_id,
                     meter_name, stats_name, unit, label=None):
    """Construct datapoint series for a meter from resource aggregates."""
    series = []
    for resource in aggregates:
        if resource.get_meter(meter_name):
            if label:
                name = label
            else:
                resource_name = ('id' if group_by == "project"
                                 else 'resource_id')
                resource_id = getattr(resource, resource_name)
                name = resource_id
            point = {'unit': unit,
                     'name': name,
                     'meter': meter_id,
                     'data': []}
            for statistic in resource.get_meter(meter_name):
                date = statistic.duration_end[:19]
                value = float(getattr(statistic, stats_name))
                point['data'].append({'x': date, 'y': value})
            series.append(point)
    return series


def get_unit(ceilometer_client, meter):
    sample_list = ceilometer_client.sample_list(meter, limit=1)
    unit = ""
    if sample_list:
        unit = sample_list[0].counter_unit
    return unit


class ProjectAggregatesQuery(object):
    def __init__(self, keystone_client, date_from, date_to,
                 period=None, additional_query=None):
        additional_query = additional_query or []
        if date_from:
            additional_query.append({'field': 'timestamp',
                                     'op': 'ge',
                                     'value': date_from})
        if date_to:
            additional_query.append({'field': 'timestamp',
                                     'op': 'le',
                                     'value': date_to})
        self.period = period
        self.additional_query = additional_query
        projects = keystone_client.get_projects()
        self.queries = {}

        for project in projects:
            project_query = [{
                             "field": "project_id",
                             "op": "eq",
                             "value": project.id}]

            self.queries[project.name] = project_query

    def query(self, ceilometer_client, meter):
        unit = get_unit(ceilometer_client, meter)
        resources = ceilometer_client.resource_aggregates_with_statistics(
            self.queries, [meter], period=self.period,
            stats_attr=None,
            additional_query=self.additional_query)
        return resources, unit


class MeterQuery(ProjectAggregatesQuery):
    def __init__(self, *args, **kwargs):
        # pop filterfunc and add it later to self.
        filterfunc = kwargs.pop('filterfunc', None)
        super(MeterQuery, self).__init__(*args, **kwargs)
        self.filterfunc = filterfunc
        # Resetting the tenant based filter set in base class
        self.queries = None

    def query(self, ceilometer_client, meter):
        def filter_by_meter_name(resource):
            """Function for filtering of the list of resources.
            Will pick the right resources according to currently selected
            meter.
            """
            for link in resource.links:
                if link['rel'] == meter:
                    # If resource has the currently chosen meter.
                    return True
            return False

        unit = get_unit(ceilometer_client, meter)

        resources = ceilometer_client.resources_with_statistics(
            self.queries, [meter],
            period=self.period,
            stats_attr=None,
            additional_query=self.additional_query,
            filter_func=filter_by_meter_name)

        return resources, unit
