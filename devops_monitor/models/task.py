from . import db

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    user = db.relationship('User', uselist=False)

    project = db.Column(db.String)
    type = db.Column(db.String)
    name = db.Column(db.String)
    definitionId = db.Column(db.Integer)
    status_time = db.Column(db.DateTime)
    sort_order = db.Column(db.Integer)

    _status_id = db.Column(db.Integer, db.ForeignKey('status.id'))
    _prev_status_id = db.Column(db.Integer, db.ForeignKey('status.id'))

    _status = db.relationship('Status', uselist=False, foreign_keys=[_status_id])
    _prev_status = db.relationship('Status', uselist=False, foreign_keys=[_prev_status_id])

    @property
    def status(self):
        return self._status.value

    @status.setter
    def status(self, new_status):
        self._prev_status = self._status
        self._status = new_status

    @property
    def prev_status(self):
        return self._prev_status.value