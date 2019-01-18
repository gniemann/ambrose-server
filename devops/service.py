from collections import namedtuple

import requests
from requests.auth import HTTPBasicAuth

Credentials = namedtuple('Credentials', ['username', 'token'])


def format_status(status: str):
    status = status.lower()
    if status == 'rejected':
        return 'failed'

    if status == 'notstarted':
        return 'queued'

    return status


class DevOpsService:
    BASE_URL_TEMPLATE = 'https://{}dev.azure.com/{}/{}/_apis/'
    RELEASE_PREFIX='vsrm'

    def __init__(self, credentials: Credentials):
        self.credentials = credentials
        self.auth = HTTPBasicAuth(credentials.username, credentials.token)

    def list_release_definitions(self, organization, project):
        endpoint = 'release/definitions?api-version=5.0-preview.3'
        return self._request(organization, project, endpoint, self.RELEASE_PREFIX)

    def get_release_summary(self, organization, project, definition_id):
        endpoint = 'release/releases?definitionId={}&releaseCount=1&api-version=5.0-preview.8'.format(definition_id)
        summary = self._request(organization, project, endpoint, self.RELEASE_PREFIX)

        if not summary:
            return {}

        pipeline_name = summary['releaseDefinition']['name']
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
                env_name = '{}_{}'.format(pipeline_name, release_env['name']).replace(' ', '_')
                env_status = format_status(release_env['status'])

                if env_status == 'inprogress':
                    if 'postDeployApprovals' in release_env:
                        approvals = release_env['postDeployApprovals']
                        if len(approvals) > 0:
                            approval = approvals[0]
                            if approval['status'] == 'pending':
                                env_status = 'pending_approval'

                statuses[env_name] = {
                    'name': env_name,
                    'status': env_status,
                    'current': release['name']
                }
                break

        return statuses

    def get_release(self, organization, project, release_id):
        endpoint = 'release/releases/{}?api-version=5.0-preview.8'.format(release_id)
        return self._request(organization, project, endpoint, self.RELEASE_PREFIX)

    def get_build_summary(self, organization, project, definition_id, branch='master'):
        endpoint = 'build/builds?api-version=5.0-preview.5&maxBuildsPerDefinition=1&definitions={}&branchName=refs/heads/{}'.format(definition_id, branch)
        summary = self._request(organization, project, endpoint)
        if not summary or len(summary['value']) < 1:
            return {}

        latest = summary['value'][0]
        name = latest['definition']['name']
        status = latest['status']
        if status == 'completed':
            status = latest['result']

        return {
            name: {
                'name': name,
                'status': format_status(status)
            }
        }

    def _get(self, url):
        return requests.get(url, auth=self.auth)

    def _request(self, organization, project, endpoint, host_prefix=''):
        if len(host_prefix) > 0 and not host_prefix.endswith('.'):
            host_prefix += '.'
        url = self.BASE_URL_TEMPLATE.format(host_prefix, organization, project) + endpoint
        res = self._get(url)
        if 200 <= res.status_code < 400:
            return res.json()

        return None
