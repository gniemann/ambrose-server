from collections import namedtuple
from datetime import datetime
from typing import Type, Optional, AnyStr, Set, Any, Mapping, Union, List

from cryptography.fernet import Fernet
from github import Github

from application_insights import ApplicationInsightsService
from devops import DevOpsService
from ambrose.common import db_transaction
from ambrose.models import DevOpsAccount, DevOpsBuildTask, DevOpsReleaseTask, Account, \
    ApplicationInsightsAccount, ApplicationInsightsMetricTask, User, GitHubAccount, GitHubRepositoryStatusTask
from .exceptions import UnauthorizedAccessException, NotFoundException

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


class AccountService:
    _model_registry = {}
    _registry = {}

    def __init_subclass__(cls, model: Type[Account], **kwargs):
        super(AccountService, cls).__init_subclass__(**kwargs)
        cls._model_registry[model.__name__] = cls
        idx = cls.__name__.index('AccountService')
        cls._registry[cls.__name__[:idx].lower()] = cls

    def __new__(cls, account: Optional[Account], cipher: Optional[Fernet] = None):
        if not account:
            return super().__new__(cls)

        service_type = cls._model_registry[account.__class__.__name__]
        return super().__new__(service_type)

    def __init__(self, account: Optional[Account], cipher: Optional[Fernet] = None):
        self.cipher = cipher
        self.account = account

    def _encrypt(self, token: str) -> str:
        return self.cipher.encrypt(token.encode('utf-8')).decode('utf-8')

    def _decrypt(self, token: AnyStr) -> str:
        if not isinstance(token, bytes):
            token = token.encode('utf-8')
        return self.cipher.decrypt(token).decode('utf-8')

    @classmethod
    def get_account(self, account_id: int, user: User) -> Account:
        account = Account.by_id(account_id)
        if account not in user.accounts:
            raise UnauthorizedAccessException()

        return account

    def get_task_statuses(self):
        pass

    @classmethod
    def create_account(cls, account_type: str, cipher: Fernet, user: User, *args, **kwargs) -> Account:
        service_type = cls._registry[account_type.lower()]
        service = service_type(None, cipher)
        return service.new_account(user, *args, **kwargs)

    def _new_account(self, *args, **kwargs) -> Account:
        pass

    def new_account(self, user: User, *args, **kwargs) -> Account:
        with db_transaction():
            account = self._new_account(*args, **kwargs)
            user.add_account(account)
            self.account = account
            return account

    def edit_account(self, *args, **kwargs):
        pass


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
        task = DevOpsReleaseTask.query.filter_by(project=project_id, definition_id=updates.definition_id, environment_id=updates.environment_id).one_or_none()

        if task is None:
            raise NotFoundException

        if task not in self.account.tasks:
            raise UnauthorizedAccessException

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


class ApplicationInsightsAccountService(AccountService, model=ApplicationInsightsAccount):
    def _new_account(self, application_id: str, api_key: str, nickname: str) -> ApplicationInsightsAccount:
        return ApplicationInsightsAccount(
            application_id=application_id,
            api_key=self._encrypt(api_key),
            nickname=nickname
        )

    def edit_account(self, application_id: str, api_key: str, nickname: str):
        with db_transaction():
            self.account.application_id = application_id
            self.account.nickname = nickname
            self.account.api_key = self._encrypt(api_key)

    def add_metric(self, metric: str, nickname: str, aggregation: str, timespan: str):
        with db_transaction():
            self.account.add_task(ApplicationInsightsMetricTask(
                metric=metric,
                nickname=nickname,
                aggregation=aggregation,
                timespan=timespan
            ))

    def get_task_statuses(self):
        insights = ApplicationInsightsService(self.account.application_id, self._decrypt(self.account.api_key))
        with db_transaction():
            for task in [t for t in self.account.tasks if isinstance(t, ApplicationInsightsMetricTask)]:
                metric = insights.get_metric(task.metric, aggregation=task.aggregation, timespan=task.timespan)
                if metric:
                    task.last_update = datetime.now()
                    task.value = metric.value
                    task.start = metric.start
                    task.end = metric.end


class GitHubAccountService(AccountService, model=GitHubAccount):
    def _new_account(self, token: str, nickname: str) -> GitHubAccount:
        return GitHubAccount(token=self._encrypt(token), nickname=nickname)

    def edit_account(self, token: str, nickname: str):
        with db_transaction():
            self.account.nickname = nickname
            self.account.token = self._encrypt(token)

    def add_repo_task(self, repo_name: str, nickname: str):
        owner, name = repo_name.split('/')

        with db_transaction():
            self.account.add_task(GitHubRepositoryStatusTask(owner=owner, repo_name=name))

    def get_task_statuses(self):
        tasks_requiring_updates = [t for t in self.account.tasks if not t.uses_webhook]
        if len(tasks_requiring_updates) == 0:
            return

        github_user = Github(self._decrypt(self.account.token)).get_user()

        with db_transaction():
            for task in tasks_requiring_updates:
                if task.owner == github_user.login:
                    repo = github_user.get_repo(task.repo_name)
                else:
                    org = [org for org in github_user.get_orgs() if org.login == task.owner][0]
                    repo = org.get_repo(task.repo_name)

                prs = list(repo.get_pulls())
                task.last_update = datetime.now()
                task.pr_count = len(prs)

                if len(prs) == 0:
                    task.status = 'no_open_prs'
                else:
                    prs_with_issues = False
                    prs_need_review = False
                    for pr in prs:
                        if not pr.mergeable:
                            prs_with_issues = True
                            break
                        reviews = list(pr.get_reviews())
                        if 'CHANGES_REQUESTED' in [review.state for review in reviews]:
                            prs_with_issues = True
                            break
                        if len(reviews) == 0:
                            prs_need_review = True

                    if prs_with_issues:
                        task.status = 'prs_with_issues'
                    elif prs_need_review:
                        task.status = 'prs_need_review'
                    else:
                        task.status = 'open_prs'

    def update_task(self, task_id: int, data: Mapping[str, Any]):
        # this is kinda cheating, but for the time being its fine.
        self.get_task_statuses()
        # task = None
        # for t in self.account.tasks:
        #     if t.repo_name == repo_name:
        #         task = t
        #         break
        #
        # if not task:
        #     raise NotFoundException

