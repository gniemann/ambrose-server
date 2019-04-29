from __future__ import annotations

from typing import Optional

from . import db


class StatusLight(db.Model):
    __tablename__ = 'status_light'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    slot = db.Column(db.Integer, primary_key=True)

    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    task = db.relationship('Task', uselist=False)

    @property
    def status(self) -> Optional[str]:
        if self.task:
            return self.task.status
        return None

    @property
    def has_changed(self) -> Optional[bool]:
        if self.task:
            return self.task.has_changed
        return None

    @classmethod
    def by_id(cls, user_id: int, slot: int) -> Optional[StatusLight]:
        return cls.query.get((user_id, slot))
