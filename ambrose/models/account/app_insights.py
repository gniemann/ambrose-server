from ambrose.models import db
from .account import Account


class ApplicationInsightsAccount(Account):
    __tablename__ = 'application_insights_account'
    description = 'Application Insights'

    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), primary_key=True)

    application_id = db.Column(db.String)
    api_key = db.Column(db.String)

    __mapper_args__ = {
        'polymorphic_identity': 'application_insights_account'
    }