from datetime import datetime
from typing import Mapping, Any

from github import Github

from ambrose.common import db_transaction
from ambrose.models import GitHubAccount, GitHubRepositoryStatusTask
from ambrose.services.accounts import AccountService


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

    def get_task_statuses(self, update_all=False):
        if update_all:
            tasks_requiring_updates = self.account.tasks
        else:
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
        watched_actions = ['opened', 'closed', 'reopened', 'submitted', 'dismissed']

        action = data['action']
        # this is kinda cheating, but for the time being its fine.
        if action in watched_actions:
            self.get_task_statuses(True)
        # task = None
        # for t in self.account.tasks:
        #     if t.repo_name == repo_name:
        #         task = t
        #         break
        #
        # if not task:
        #     raise NotFoundException
