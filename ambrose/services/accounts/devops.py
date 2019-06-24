from datetime import datetime
from typing import Set, List, Union, Mapping, Any, Tuple, Iterable

from ambrose.common import db_transaction
from ambrose.models import DevOpsAccount, DevOpsReleaseTask, DevOpsBuildTask
from ambrose.services import NotFoundException, UnauthorizedAccessException
from ambrose.services.accounts import AccountService
from devops import DevOpsService


class BuildTask:
    def __init__(self, project, definition_id, **kwargs):
        self.project = project
        self.definition_id = int(definition_id)
        self.current = False
        for key, val in kwargs.items():
            self.__setattr__(key, val)

    def __eq__(self, other):
        return self.project == other.project and self.definition_id == other.definition_id

    def __hash__(self):
        return hash(self.project + str(self.definition_id))


class ReleaseTask:
    def __init__(self, project, definition_id, environment_id, **kwargs):
        self.project = project
        self.definition_id = int(definition_id)
        self.environment_id = int(environment_id)
        self.current = False
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
            pipeline=t.pipeline,
            current=True
        ) for t in self.account.build_tasks}

    @property
    def release_tasks(self) -> Set[ReleaseTask]:
        return {ReleaseTask(
            project=t.project,
            definition_id=t.definition_id,
            environment_id=t.environment_id,
            pipeline=t.pipeline,
            environment=t.environment,
            uses_webhook=t.uses_webhook,
            current=True
        ) for t in self.account.release_tasks}

    def get_service(self) -> DevOpsService:
        token = self._decrypt(self.account.token)
        return DevOpsService(self.account.username, token, self.account.organization)

    def list_all_tasks(self) -> Tuple[List[BuildTask], List[ReleaseTask]]:
        service = self.get_service()
        project_list = service.list_projects()
        if not project_list:
            return [], []  # TODO: raise exception instead

        builds = set()
        releases = set()
        for project in [p.name for p in project_list]:
            builds.update(self._list_builds(service, project))
            releases.update(self._list_releases(service, project))

        return sorted(builds, key=lambda x: (x.project, x.pipeline)), \
               sorted(releases, key=lambda x: (x.project, x.pipeline, x.environment))

    def _list_releases(self, service: DevOpsService, project: str) -> Set[ReleaseTask]:
        release_list = service.list_release_definitions(project)
        if release_list:
            releases = set()
            for release in release_list:
                for environment in release.environments:
                    releases.add(ReleaseTask(
                        project=project,
                        definition_id=int(release.id),
                        environment_id=int(environment.id),
                        pipeline=release.name,
                        environment=environment.name,
                        uses_webhook=False
                    ))

            # get the release tasks that are current (the intersection of the current task and the retrieved tasks
            # this ensures that current and webhooks are set appropriately
            # then get the new releases - the new tasks - the current tasks
            # add the union of these to the releases
            current_releases = self.release_tasks.intersection(releases)
            new_releases = releases.difference(current_releases)
            return current_releases.union(new_releases)

    def _list_builds(self, service: DevOpsService, project: str) -> Set[BuildTask]:
        build_list = service.list_build_definitions(project)
        if build_list:
            builds = set()
            for build in build_list:
                builds.add(BuildTask(
                    project=project,
                    definition_id=int(build.id),
                    pipeline=build.name,
                ))

            # same process as with releases
            current_builds = self.build_tasks.intersection(builds)
            new_builds = builds.difference(current_builds)
            return current_builds.union(new_builds)

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
        task = self.get_release_task(project_id, updates.definition_id, updates.environment_id)

        if task is None:
            raise NotFoundException()

        if task not in self.account.tasks:
            raise UnauthorizedAccessException()

        with db_transaction():
            task.status = updates.status
            task.last_update = datetime.now()

    def get_release_task(self, project_id: str, definition_id: str, environment_id: str):
        task = DevOpsReleaseTask.query.filter_by(project_id=project_id, definition_id=definition_id,
                                                 environment_id=int(environment_id)).one_or_none()

        if not task or task not in self.account.tasks:
            return None

        return task

    def update_build_tasks(self, data: Iterable[Mapping[str, Any]]):
        new_build_tasks = {BuildTask(**t) for t in data}

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
                    pipeline=task.pipeline
                ))

    def update_release_tasks(self, data: Iterable[Mapping[str, Any]]):
        new_release_tasks = {ReleaseTask(**t) for t in data}

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
                    pipeline=task.pipeline,
                    environment=task.environment,
                    environment_id=task.environment_id,
                    uses_webhook=task.uses_webhook
                ))

            # tasks to edit - order matters in this set operation and new_release_tasks must be second
            for t in current_release_tasks.intersection(new_release_tasks):
                for task in self.account.tasks:
                    if task != t:
                        continue

                    task.uses_webhook = t.uses_webhook
                    break
