from typing import Optional, Iterable, Type, TypeVar

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

    def list_release_definitions(self, project: str) -> Optional[DevOpsReleaseDefinitions]:
        endpoint = 'release/definitions?api-version=5.0-preview.3&$expand=Environments'
        return self._request(project, endpoint, self.RELEASE_PREFIX, return_type=DevOpsReleaseDefinitions)

    def list_build_definitions(self, project: str) -> Optional[DevOpsBuildDefinitions]:
        endpoint = 'build/definitions?api-version=5.0'
        return self._request(project, endpoint, return_type=DevOpsBuildDefinitions)

    def get_release_summary(self, project: str, definition_id: int) -> Optional[ReleaseSummary]:
        endpoint = 'release/releases?definitionId={}&releaseCount=1&api-version=5.0-preview.8'.format(definition_id)
        return self._request(project, endpoint, self.RELEASE_PREFIX, return_type=ReleaseSummary)

    def get_release(self, project: str, release_id: int) -> Optional[DevOpsJSON]:
        endpoint = 'release/releases/{}?api-version=5.0-preview.8'.format(release_id)
        return self._request(project, endpoint, self.RELEASE_PREFIX)

    def get_release_definition(self, project: str, definition_id: int) -> Optional[DevOpsJSON]:
        endpoint = 'release/definitions/{}?api-version=5.0'.format(definition_id)
        return self._request(project, endpoint, self.RELEASE_PREFIX)

    def get_build_summary(self, project: str, definition_ids: Iterable[int], branch: str = 'master') -> Optional[
        BuildSummary]:
        ids = ','.join([str(i) for i in definition_ids])

        endpoint = 'build/builds?api-version=5.0-preview.5&maxBuildsPerDefinition=1&definitions={}&branchName=refs/heads/{}'.format(
            ids, branch)
        return self._request(project, endpoint, return_type=BuildSummary)

    def list_projects(self) -> Optional[DevOpsProjects]:
        endpoint = 'projects?api-version=5.0'
        url = 'https://dev.azure.com/{}/_apis/{}'.format(self.organization, endpoint)
        res = self._get(url)
        if 200 <= res.status_code < 400:
            return DevOpsProjects(res.json())
        return None

    def _get(self, url: str) -> requests.Response:
        return requests.get(url, auth=self.auth)

    T = TypeVar('T', bound=DevOpsJSON)

    def _request(self, project: str, endpoint: str, host_prefix: str = '', return_type: Type[T] = DevOpsJSON) -> T:
        if len(host_prefix) > 0 and not host_prefix.endswith('.'):
            host_prefix += '.'
        url = self.BASE_URL_TEMPLATE.format(host_prefix, self.organization, project) + endpoint
        res = self._get(url)
        if 200 <= res.status_code < 400:
            return return_type(res.json())

        return None
