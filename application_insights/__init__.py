from numbers import Number

import requests
from dateutil import parser

from json_object import JSONObject


class MetricJSON(JSONObject):
    def __init__(self, json):
        super(MetricJSON, self).__init__(json['value'])


class Metric:
    def __init__(self, json, metric):
        metric = metric.replace('/', '_')
        # this should be a dictionary one 1 pair
        for key, val in json[metric].items():
            setattr(self, key, val)
            self.value_type = key
            if isinstance(val, Number):
                val = int(val)
            self.value = val

        self.start = parser.parse(json.start)
        self.end = parser.parse(json.end)


class ApplicationInsightsService:
    BASE_URL_TEMPLATE = 'https://api.applicationinsights.io/v1/apps/{}/'

    def __init__(self, application_id, api_key):
        self.application_id = application_id
        self.api_key = api_key

    def get_request_duration(self):
        return self.get_metric('requests/duration')

    def get_metric(self, metric, aggregation=None, timespan=None):
        """
        Queries Application Insights for the requested metric. If provided, adds aggregation and timespan to the query.
        If the optional arguments are None, they are not sent as part of the query and the application insights defaults
        are used.
        :param metric: the metric to retrieve, in the form of 'requests/duration'
        :param aggregation: Optional, what aggregate to use (ie, avg, sum, etc).
        :param timespan: Optional, what timespan to use. See app insights REST API documentation.
        :return: Returns a Metric object if successful, or None if unsuccessful
        """
        endpoint = 'metrics/{}'.format(metric)
        query = []
        if aggregation:
            query.append('aggregation={}'.format(aggregation))
        if timespan:
            query.append('timespan={}'.format(timespan))

        if len(query) > 0:
            endpoint += '?' + '&'.join(query)

        json = self._request(endpoint)
        if json:
            return Metric(json, metric)
        return None

    def _get(self, url):
        return requests.get(url, headers={'x-api-key': self.api_key})

    def _request(self, endpoint):
        url = self.BASE_URL_TEMPLATE.format(self.application_id) + endpoint
        res = self._get(url)
        if 200 <= res.status_code < 400:
            return MetricJSON(res.json())

        return None
