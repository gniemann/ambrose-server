from . import db


class StatusLight(db.Model):
    __tablename__ = 'status_light'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    slot = db.Column(db.Integer, primary_key=True)

    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    task = db.relationship('Task', uselist=False)

    @property
    def status(self):
        if self.task:
            return self.task.status
        return None

    @property
    def has_changed(self):
        if self.task:
            return self.task.has_changed
        return None

    @classmethod
    def by_id(cls, user_id, slot):
        return cls.query.get((user_id, slot))
