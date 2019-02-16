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
    def __init__(self, json):
        super(ReleaseSummary, self).__init__(json)
        if 'releases' in json:
            self._data['releases'] = {rel.id: rel for rel in json['releases']}

    def status(self):
        pipeline_name = self.releaseDefinition.name

        statuses = {}
        for env in self.environments:
            last_release = env.lastReleases
            if not last_release or len(last_release) < 1:
                continue

            last_release_id = last_release[0].id

            release = self.releases[last_release_id]

            release_env = [rel_env for rel_env in release.environments if rel_env.definitionEnvironmentId == env.id]
            if len(release_env) < 1:
                continue

            release_env = release_env[0]

            env_name = '{}_{}'.format(pipeline_name, release_env.name).replace(' ', '_')
            env_status = self._format_status(release_env)

            statuses[env_name] = ReleaseStatus(name=env_name, status=env_status, current=release.name)

        return statuses

    def _format_status(self, environment):
        status = format_status(environment.status)

        if status == 'inprogress':
            if 'postDeployApprovals' in environment:
                approvals = environment.postDeployApprovals
                if len(approvals) > 0:
                    approval = approvals[0]
                    if approval.status == 'pending':
                        status = 'pending_approval'

        return status

    def status_for_environment(self, env_id):
        environment = None
        for env in self.environments:
            if env.id == env_id:
                environment = env
                break

        if environment is None:
            return None

        last_release = environment.lastReleases
        if not last_release or len(last_release) < 1:
            return None

        release = self.releases[last_release[0].id]

        release_env = None
        for env in release.environments:
            if env.definitionEnvironmentId == env_id:
                release_env = env
                break
        if release_env is None:
            return None

        return self._format_status(release_env)

    def environment_names(self):
        environments = []
        for env in self.environments:
            last_release = env.lastReleases
            if not last_release or len(last_release) < 1:
                continue

            last_release_id = last_release[0].id

            release = self.releases[last_release_id]

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

    def status_for_definition(self, definition_id):
        target_build = None
        for build in self.value:
            if build.definition.id == definition_id:
                target_build = build
                break
        if target_build is None:
            return None

        status = target_build.status
        if status == 'completed':
            status = target_build.result

        return status


class DevOpsProjects(DevOpsJSON):
    def __init__(self, json):
        super(DevOpsProjects, self).__init__({"projects": json['value']})

    def __iter__(self):
        return iter(self.projects)

class DevOpsReleaseDefinitions(DevOpsJSON):
    def __init__(self, json):
        super(DevOpsReleaseDefinitions, self).__init__({'definitions': json['value']})

    def __iter__(self):
        return iter(self.definitions)


class DevOpsBuildDefinitions(DevOpsJSON):
    def __init__(self, json):
        super(DevOpsBuildDefinitions, self).__init__({'builds': json['value']})

    def __iter__(self):
        return iter(self.builds)