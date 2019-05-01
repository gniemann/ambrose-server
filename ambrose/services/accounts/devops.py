from collections import namedtuple
from datetime import datetime
from typing import Set, List, Union, Mapping, Any

from ambrose.common import db_transaction
from ambrose.models import DevOpsAccount, DevOpsReleaseTask, DevOpsBuildTask
from ambrose.services import NotFoundException, UnauthorizedAccessException
from ambrose.services.accounts import AccountService
from devops import DevOpsService

BuildTask = namedtuple('BuildTask', 'project definition_id name type')


class ReleaseTask:
    def __init__(self, **kwargs):
        self.type = 'release'
        for key, val in kwargs.items():
            self.__setattr__(key, val)

    def __eq__(self, other):
        return other.project == self.project and \
               other.definition_id == self.definition_id and \
               other.environment_id == self.environment_id

    def __hash__(self):
        return hash(self.project + str(self.definition_id) + str(self.environment_id))


class DevOpsAccountService(AccountService, model=DevOpsAccount):
    def _new_account(self, username: str, organization: str, token: str, nickname: str) -> DevOpsAccount:
        return DevOpsAccount(
            username=username,
            organization=organization,
            token=self._encrypt(token),
            nickname=nickname
        )

    def edit_account(self, username: str, organization: str, token: str, nickname: str):
        with db_transaction():
            self.account.username = username
            self.account.organization = organization
            self.account.nickname = nickname

            if len([c for c in token if c != '*']) > 0:
                self.account.token = self._encrypt(token)

    @property
    def build_tasks(self) -> Set[BuildTask]:
        return {BuildTask(
            project=t.project,
            definition_id=t.definition_id,
            name=t.pipeline,
            type='build'
        ) for t in self.account.build_tasks}

    @property
    def release_tasks(self) -> Set[ReleaseTask]:
        return {ReleaseTask(
            project=t.project,
            definition_id=t.definition_id,
            name=t.pipeline,
            environment=t.environment,
            environment_id=t.environment_id,
            uses_webhook=t.uses_webhook
        ) for t in self.account.release_tasks}

    def get_service(self) -> DevOpsService:
        token = self._decrypt(self.account.token)
        return DevOpsService(self.account.username, token, self.account.organization)

    def list_all_tasks(self) -> List[Union[BuildTask, ReleaseTask]]:
        tasks = []
        service = self.get_service()
        project_list = service.list_projects()
        if not project_list:
            return []  # TODO: raise exception instead

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
                            uses_webhook=False
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

    def get_task_statuses(self):
        with db_transaction():
            self.update_build_statuses()
            self.update_release_statuses()

    def update_build_statuses(self):
        builds = self.account.build_tasks
        service = self.get_service()

        with db_transaction():
            for project in {b.project for b in builds}:
                project_builds = [b for b in builds if b.project == project]
                definitions = [b.definition_id for b in project_builds]
                statuses = service.get_build_summary(project, definitions)
                update_time = datetime.now()

                for build in project_builds:
                    build.status = statuses.status_for_definition(build.definition_id)
                    build.last_update = update_time

    def update_release_statuses(self):
        # filter out the releases that use web hooks
        releases = [r for r in self.account.release_tasks if not r.uses_webhook]
        service = self.get_service()

        with db_transaction():
            for (project, definition) in {(t.project, t.definition_id) for t in releases}:
                statuses = service.get_release_summary(project, definition)
                update_time = datetime.now()
                for env in [r for r in releases if r.project == project and r.definition_id == definition]:
                    env.status = statuses.status_for_environment(env.environment_id)
                    env.last_update = update_time

    def update_release_with_data(self, project_id, updates):
        task = DevOpsReleaseTask.query.filter_by(project=project_id, definition_id=updates.definition_id,
                                                 environment_id=updates.environment_id).one_or_none()

        if task is None:
            raise NotFoundException()

        if task not in self.account.tasks:
            raise UnauthorizedAccessException()

        with db_transaction():
            task.status = updates.status
            task.last_update = datetime.now()

    def update_build_tasks(self, data: List[Mapping[str, Any]]):
        new_build_tasks = {BuildTask(
            project=t['project'],
            definition_id=t['definition_id'],
            name=t['pipeline'],
            type='build'
        ) for t in data}

        current_build_tasks = self.build_tasks

        with db_transaction():
            # build tasks to remove
            for task in current_build_tasks.difference(new_build_tasks):
                self.account.remove_task(task)

            # build tasks to add
            for task in new_build_tasks.difference(current_build_tasks):
                self.account.add_task(DevOpsBuildTask(
                    project=task.project,
                    definition_id=task.definition_id,
                    pipeline=task.name
                ))

    def update_release_tasks(self, data: List[Mapping[str, Any]]):
        new_release_tasks = {ReleaseTask(
            project=t['project'],
            definition_id=int(t['definition_id']),
            name=t['pipeline'],
            environment=t['environment'],
            environment_id=int(t['environment_id']),
            uses_webhook=t['uses_webhook']
        ) for t in data}

        current_release_tasks = self.release_tasks

        with db_transaction():
            # release tasks to remove
            for task in current_release_tasks.difference(new_release_tasks):
                self.account.remove_task(task)

            # release tasks to add
            for task in new_release_tasks.difference(current_release_tasks):
                self.account.add_task(DevOpsReleaseTask(
                    project=task.project,
                    definition_id=task.definition_id,
                    pipeline=task.name,
                    environment=task.environment,
                    environment_id=task.environment_id,
                    uses_webhook=task.uses_webhook
                ))
