from . import db


class Gauge(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))

    min_val = db.Column(db.Integer)
    max_val = db.Column(db.Integer)
    nickname = db.Column(db.String)

    task = db.relationship('Task', uselist=False)

    @property
    def position(self):
        upper_bound = self.max_val - self.min_val
        normalized_val = min(int(self.task.value) - self.min_val, upper_bound)
        return max(0, normalized_val / upper_bound)

    @property
    def name(self):
        return self.nickname if len(self.nickname) > 0 else self.task.name
