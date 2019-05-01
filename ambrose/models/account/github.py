from ambrose.models import db
from .account import Account


class GitHubAccount(Account):
    __tablename__ = 'github_account'
    __mapper_args__ = {
        'polymorphic_identity': 'github_account'
    }
    description = 'GitHub'

    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), primary_key=True)

    token = db.Column(db.String)