import requests

from json_object import JSONObject

class MetricJSON(JSONObject):
    def __init__(self, json):
        super(MetricJSON, self).__init__(json['value'])


class ApplicationInsightsService:
    BASE_URL_TEMPLATE = 'https://api.applicationinsights.io/v1/apps/{}/'

    def __init__(self, application_id, api_key):
        self.application_id = application_id
        self.api_key = api_key

    def get_request_duration(self):
        endpoint = 'metrics/requests/duration'
        return self._request(endpoint)

    def _get(self, url):
        return requests.get(url, headers={'x-api-key': self.api_key})

    def _request(self, endpoint):
        url = self.BASE_URL_TEMPLATE.format(self.application_id) + endpoint
        res = self._get(url)
        if 200 <= res.status_code < 400:
            return MetricJSON(res.json())

        return res