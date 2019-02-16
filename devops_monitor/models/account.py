from . import db, Task


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    type = db.Column(db.String)
    nickname = db.Column(db.String)

    user = db.relationship('User', back_populates='accounts')
    tasks = db.relationship('Task', back_populates='account')

    __mapper_args__ = {
        'polymorphic_identity': 'account',
        'polymorphic_on': type
    }

    @classmethod
    def by_id(cls, account_id):
        return cls.query.get(account_id)

    def add_task(self, task):
        if isinstance(task, Task):
            task.user_id = self.user_id
            self.tasks.append(task)

    def remove_task(self, task):
        if isinstance(task, Task):
            self.tasks.remove(task)


class DevOpsAccount(Account):
    __tablename__ = 'devops_account'
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), primary_key=True)

    username = db.Column(db.String)
    organization = db.Column(db.String)
    token = db.Column(db.String)

    __mapper_args__ = {
        'polymorphic_identity': 'devops_account'
    }

    def remove_task(self, task):
        if isinstance(task, Task):
            super(DevOpsAccount, self).remove_task(task)
        else:
            for t in self.tasks:
                if t == task:
                    self.tasks.remove(t)