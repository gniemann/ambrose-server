from collections import namedtuple

from devops import DevOpsService
from devops_monitor.common import db_transaction
from devops_monitor.models import DevOpsAccount, DevOpsBuildPipeline, DevOpsReleaseEnvironment, Account

BuildTask = namedtuple('BuildTask', 'project definition_id name type')
ReleaseTask = namedtuple('ReleaseTask', 'project definition_id name environment environment_id type')

class UnauthorizedAccessException(Exception):
    pass

class AccountService:
    def __init__(self, cipher=None):
        self.cipher = cipher

    def get_account(self, account_id, user):
        account = Account.by_id(account_id)
        if account not in user.accounts:
            raise UnauthorizedAccessException()

        return account

class DevOpsAccountService(AccountService):
    def new_account(self, user, username, organization, token, nickname):
        token = self.cipher.encrypt(token.encode('utf-8'))

        account = DevOpsAccount(
            username=username,
            organization=organization,
            token=token,
            nickname=nickname
        )

        with db_transaction():
            user.add_account(account)


    def build_tasks(self, account):
        return {BuildTask(
            project=t.project,
            definition_id=t.definition_id,
            name=t.pipeline,
            type='build'
     ) for t in account.build_tasks}


    def release_tasks(self, account):
        return {ReleaseTask(
            project=t.project,
            definition_id=t.definition_id,
            name=t.pipeline,
            environment=t.environment,
            environment_id=t.environment_id,
            type='release'
    ) for t in account.release_tasks}


    def update_tasks(self, account, data):
        new_build_tasks = {BuildTask(
            project=properties['project'],
            definition_id=int(properties['definition_id']),
            name=properties['name'],
            type='build'
        ) for key, properties in data.items() if key.startswith('build')}

        new_release_tasks = {ReleaseTask(
            project=properties['project'],
            definition_id=int(properties['definition_id']),
            name=properties['name'],
            environment=properties['environment'],
            environment_id=int(properties['environment_id']),
            type='release'
        ) for key, properties in data.items() if key.startswith('release')}

        current_build_tasks = self.build_tasks(account)
        current_release_tasks = self.release_tasks(account)

        with db_transaction():
            # build tasks to remove
            for task in current_build_tasks.difference(new_build_tasks):
                account.remove_task(task)

            # build tasks to add
            for task in new_build_tasks.difference(current_build_tasks):
                account.add_task(DevOpsBuildPipeline(
                    project=task.project,
                    definition_id=task.definition_id,
                    pipeline=task.name
                ))

            #release tasks to remove
            for task in current_release_tasks.difference(new_release_tasks):
                account.remove_task(task)

            # release tasks to add
            for task in new_release_tasks.difference(current_release_tasks):
                account.add_task(DevOpsReleaseEnvironment(
                    project=task.project,
                    definition_id=task.definition_id,
                    pipeline=task.name,
                    environment=task.environment,
                    environment_id=task.environment_id
                ))

    def get_service(self, account):
        token = self.cipher.decrypt(account.token)
        return DevOpsService(account.username, token, account.organization)

    def list_all_tasks(self, account):
        tasks = []
        service = self.get_service(account)
        project_list = service.list_projects()
        if not project_list:
            return [] # TODO: raise exception instead

        for project in [p.name for p in project_list]:
            release_list = service.list_release_definitions(project)
            if release_list:
                for release in release_list:
                    for environment in release.environments:
                        tasks.append(ReleaseTask(
                            project=project,
                            definition_id=int(release.id),
                            name=release.name,
                            environment=environment.name,
                            environment_id=int(environment.id),
                            type='release'
                        ))

            build_list = service.list_build_definitions(project)
            if build_list:
                for build in build_list:
                    tasks.append(BuildTask(
                        project=project,
                        definition_id=int(build.id),
                        name=build.name,
                        type='build'
                    ))

        return tasks

    def get_task_statuses(self, account):
        with db_transaction():
            self.update_build_statuses(account)
            self.update_release_statuses(account)

    def update_build_statuses(self, account):
        builds = account.build_tasks
        service = self.get_service(account)

        with db_transaction():
            for project in {b.project for b in builds}:
                project_builds = [b for b in builds if b.project == project]
                definitions = [b.definition_id for b in project_builds]
                statuses = service.get_build_summary(project, definitions)

                for build in project_builds:
                    build.status = statuses.status_for_definition(build.definition_id)

    def update_release_statuses(self, account):
        releases = account.release_tasks
        service = self.get_service(account)

        with db_transaction():
            for (project, definition) in {(t.project, t.definition_id) for t in releases}:
                statuses = service.get_release_summary(project, definition)
                for env in [r for r in releases if r.project == project and r.definition_id == definition]:
                    env.status = statuses.status_for_environment(env.environment_id)