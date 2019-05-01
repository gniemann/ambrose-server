from datetime import datetime
from typing import Mapping, Any

from github import Github

from ambrose.common import db_transaction
from ambrose.models import GitHubAccount, GitHubRepositoryStatusTask
from ambrose.services import NotFoundException, UnauthorizedAccessException
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
                    task.status = self._status_for_prs(prs)

    def _status_for_prs(self, prs):
        prs_need_review = False
        for pr in prs:
            if not pr.mergeable:
                return 'prs_with_issues'

            reviews = list(pr.get_reviews())
            if 'CHANGES_REQUESTED' in [review.state for review in reviews]:
                return 'prs_with_issues'
            if len(reviews) == 0:
                prs_need_review = True

        return 'prs_need_review' if prs_need_review else 'open_prs'

    def update_task(self, task_id: int, data: Mapping[str, Any]):
        task = GitHubRepositoryStatusTask.by_id(task_id)
        if not task:
            raise NotFoundException()

        if task not in self.account.tasks:
            raise UnauthorizedAccessException()

        action = data['action']

        # there are some that we don't care about - just ignore them
        unwatched_actions = ['assigned', 'unassigned', 'review_requested', 'review_requested_removed', 'labeled', 'unlabeled', 'ready_for_review', 'locked', 'unlocked']
        if action in unwatched_actions:
            return

        # if the action is open and there are no other PRs, increment the count and set the status to
        # PRs needing review
        if action == 'opened':
            with db_transaction():
                task.pr_count += 1
                task.last_update = datetime.now()

                if task.status == 'no_open_prs' or task.status == 'open_prs':
                    task.tatus = 'prs_need_review'
            return

        # if the action is closed, decrement the count. If there are no more PRs, set the status
        if action == 'closed':
            with db_transaction():
                task.pr_count -= 1
                if task.pr_count == 0:
                    task.status = 'no_open_prs'
                task.last_update = datetime.now()
            return

        # for right now, just going to punt the rest of them
        self.get_task_statuses(True)
