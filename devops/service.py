import requests
from requests.auth import HTTPBasicAuth

from devops.devops_json import DevOpsJSON, ReleaseSummary, BuildSummary, DevOpsReleaseDefinitions, \
    DevOpsBuildDefinitions, DevOpsProjects


class DevOpsService:
    BASE_URL_TEMPLATE = 'https://{}dev.azure.com/{}/{}/_apis/'
    RELEASE_PREFIX = 'vsrm'

    def __init__(self, username, token, organization):
        self.auth = HTTPBasicAuth(username, token)
        self.organization = organization

    def list_release_definitions(self, project):
        endpoint = 'release/definitions?api-version=5.0-preview.3&$expand=Environments'
        return self._request(project, endpoint, self.RELEASE_PREFIX, return_type=DevOpsReleaseDefinitions)

    def list_build_definitions(self, project):
        endpoint = 'build/definitions?api-version=5.0'
        return self._request(project, endpoint, return_type=DevOpsBuildDefinitions)

    def get_release_summary(self, project, definition_id):
        endpoint = 'release/releases?definitionId={}&releaseCount=1&api-version=5.0-preview.8'.format(definition_id)
        return self._request(project, endpoint, self.RELEASE_PREFIX, return_type=ReleaseSummary)

    def get_release(self, project, release_id):
        endpoint = 'release/releases/{}?api-version=5.0-preview.8'.format(release_id)
        return self._request(project, endpoint, self.RELEASE_PREFIX)

    def get_release_definition(self, project, definition_id):
        endpoint = 'release/definitions/{}?api-version=5.0'.format(definition_id)
        return self._request(project, endpoint, self.RELEASE_PREFIX)

    def get_build_summary(self, project, definition_ids, branch='master'):
        ids = ','.join([str(i) for i in definition_ids])

        endpoint = 'build/builds?api-version=5.0-preview.5&maxBuildsPerDefinition=1&definitions={}&branchName=refs/heads/{}'.format(
            ids, branch)
        return self._request(project, endpoint, return_type=BuildSummary)

    def list_projects(self):
        endpoint = 'projects?api-version=5.0'
        url = 'https://dev.azure.com/{}/_apis/{}'.format(self.organization, endpoint)
        res = self._get(url)
        if 200 <= res.status_code < 400:
            return DevOpsProjects(res.json())
        return None

    def _get(self, url):
        return requests.get(url, auth=self.auth)

    def _request(self, project, endpoint, host_prefix='', return_type=DevOpsJSON):
        if len(host_prefix) > 0 and not host_prefix.endswith('.'):
            host_prefix += '.'
        url = self.BASE_URL_TEMPLATE.format(host_prefix, self.organization, project) + endpoint
        res = self._get(url)
        if 200 <= res.status_code < 400:
            return return_type(res.json())

        return None
