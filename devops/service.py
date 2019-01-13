from collections import namedtuple

import requests
from requests.auth import HTTPBasicAuth

Credentials = namedtuple('Credentials', ['username', 'token'])

def format_status(status: str):
    status = status.lower()
    if status == 'rejected':
        return 'failed'

    return status

class DevOpsService:
    BASE_URL_TEMPLATE = 'https://vsrm.dev.azure.com/{}/{}/_apis/'

    def __init__(self, credentials: Credentials):
        self.credentials = credentials
        self.auth = HTTPBasicAuth(credentials.username, credentials.token)

    def list_release_definitions(self, organization, project):
        endpoint = 'release/definitions?api-version=5.0-preview.3'
        return self._request(organization, project, endpoint)

    def get_release_summary(self, organization, project, definitionId):
        endpoint = 'release/releases?definitionId={}&releaseCount=1&api-version=5.0-preview.8'.format(definitionId)
        summary = self._request(organization, project, endpoint)

        releases = {rel['id']: rel for rel in summary['releases']}

        statuses = {}
        for env in summary['environments']:
            last_release = env['lastReleases']
            if not last_release or len(last_release) < 1:
                continue

            last_release_id = last_release[0]['id']

            release = releases[last_release_id]

            for release_env in release['environments']:
                if release_env['definitionEnvironmentId'] != env['id']:
                    continue
                env_name = release_env['name']
                env_status = release_env['status']

                statuses[env_name] = {
                    'name': env_name,
                    'status': env_status,
                    'current': release['name']
                }
                break

        return statuses


    def get_release(self, organization, project, id):
        endpoint = 'release/releases/{}?api-version=5.0-preview.8'.format(id)
        return self._request(organization, project, endpoint)

    def get(self, url):
        return requests.get(url, auth=self.auth)

    def _request(self, organization, project, endpoint):
        url = self.BASE_URL_TEMPLATE.format(organization, project) + endpoint
        res = self.get(url)
        if res.status_code >= 200 and res.status_code < 400:
            return res.json()

        return None
