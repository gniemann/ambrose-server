from . import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.String)
    organization = db.Column(db.String)
    token = db.Column(db.String)

    tasks = db.relationship('Task', back_populates='user', order_by='Task.sort_order', cascade='all, delete, delete-orphan')
    messages = db.relationship('Message', cascade='all, delete, delete-orphan')

    @classmethod
    def by_username(cls, username):
        return cls.query.filter_by(username=username).one_or_none()

    def remove_tasks(self, tasknamess_to_remove):
        for task in set([t for t in self.tasks if t.name in tasknamess_to_remove]):
            self.tasks.remove(task)

    def add_tasks(self, tasks):
        self.tasks.extend(tasks)