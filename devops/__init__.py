from collections import namedtuple

from .service import DevOpsService, Credentials


ReleaseStatus = namedtuple('ReleaseStatus', 'name status current')
BuildStatus = namedtuple('BuildStatus', 'name status')

def format_status(status: str):
    status = status.lower()
    if status == 'rejected':
        return 'failed'

    if status == 'notstarted':
        return 'queued'

    return status

def determine_release_statuses(summary):
    if not summary:
        return {}

    pipeline_name = summary.releaseDefinition.name
    releases = {rel.id: rel for rel in summary.releases }

    statuses = {}
    for env in summary.environments:
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


def determine_build_statuses(summary):
    if not summary or len(summary.value) < 1:
        return {}

    statuses = {}
    for val in summary.value:
        name = val.definition.name
        status = val.status
        if status == 'completed':
            status = val.result
        statuses[name] = BuildStatus(name=name, status=format_status(status))

    return statuses