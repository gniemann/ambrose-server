import keyword
from collections import abc, namedtuple

ReleaseStatus = namedtuple('ReleaseStatus', 'name status current')
BuildStatus = namedtuple('BuildStatus', 'name status')

def format_status(status: str):
    status = status.lower()
    if status == 'rejected':
        return 'failed'

    if status == 'notstarted':
        return 'queued'

    return status

class DevOpsJSON:
    def __new__(cls, arg):
        if isinstance(arg, abc.Mapping):
            return super().__new__(cls)
        elif isinstance(arg, abc.MutableSequence):
            return [cls(item) for item in arg]
        else:
            return arg

    def __init__(self, wrapped):
        self._data = {}

        for key, value in wrapped.items():
            if keyword.iskeyword(key):
                key += '_'
            self._data[key] = value

    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]
        if hasattr(self._data, item):
            return getattr(self._data, item)
        return DevOpsJSON(self._data[item])

    def __getitem__(self, item):
        return self._data[item]


class ReleaseSummary(DevOpsJSON):
    def status(self):
        pipeline_name = self.releaseDefinition.name
        releases = {rel.id: rel for rel in self.releases}

        statuses = {}
        for env in self.environments:
            last_release = env.lastReleases
            if not last_release or len(last_release) < 1:
                continue

            last_release_id = last_release[0].id

            release = releases[last_release_id]

            release_env = [rel_env for rel_env in release.environments if rel_env.definitionEnvironmentId == env.id]
            if len(release_env) < 1:
                continue

            release_env = release_env[0]

            env_name = '{}_{}'.format(pipeline_name, release_env.name).replace(' ', '_')
            env_status = format_status(release_env.status)

            if env_status == 'inprogress':
                if 'postDeployApprovals' in release_env:
                    approvals = release_env.postDeployApprovals
                    if len(approvals) > 0:
                        approval = approvals[0]
                        if approval.status == 'pending':
                            env_status = 'pending_approval'

            statuses[env_name] = ReleaseStatus(name=env_name, status=env_status, current=release.name)

        return statuses

    def environment_names(self):
        releases = {rel.id: rel for rel in self.releases}

        environments = []
        for env in self.environments:
            last_release = env.lastReleases
            if not last_release or len(last_release) < 1:
                continue

            last_release_id = last_release[0].id

            release = releases[last_release_id]

            release_env = [rel_env for rel_env in release.environments if rel_env.definitionEnvironmentId == env.id]
            if len(release_env) < 1:
                continue

            release_env = release_env[0]

            environments.append('{}_{}'.format(self.releaseDefinition.name, release_env.name).replace(' ', '_'))

        return environments



class BuildSummary(DevOpsJSON):
    def status(self):
        statuses = {}
        for val in self.value:
            name = val.definition.name
            status = val.status
            if status == 'completed':
                status = val.result
            statuses[name] = BuildStatus(name=name, status=format_status(status))

        return statuses
