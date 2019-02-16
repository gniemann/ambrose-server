from . import db, DevOpsAccount


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.String)

    accounts = db.relationship('Account', back_populates='user')

    tasks = db.relationship('Task', back_populates='user', order_by='Task.sort_order', cascade='all, delete, delete-orphan')
    messages = db.relationship('Message', cascade='all, delete, delete-orphan')

    @classmethod
    def by_username(cls, username):
        return cls.query.filter_by(username=username).one_or_none()

    @property
    def devops_account(self):
        for account in self.accounts:
            if isinstance(account, DevOpsAccount):
                return account
        return None
