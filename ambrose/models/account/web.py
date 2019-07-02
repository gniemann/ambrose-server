from ambrose.models import db
from . import Account


class WebAccount(Account):
    __tablename__ = 'web_account'
    __mapper_args__ = {
        'polymorphic_identity': 'web_account'
    }

    description = 'Web API Account'

    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), primary_key=True)

    base_url = db.Column(db.String)