from flask import jsonify, abort, Blueprint
from flask.views import MethodView
from flask_jwt_extended import jwt_required

from ambrose.api import TaskSchema
from ambrose.services import AuthService, UserService

api_tasks_bp = Blueprint('devices_api', __name__)


class Tasks(MethodView):
    decorators = [jwt_required]

    def get(self):
        pass

    def get(self, task_id):
        user = AuthService.current_api_user()
        if task_id is None:
            retval = TaskSchema().dump(user.tasks, many=True)
        else:
            msg = UserService(user).get_task(task_id)
            retval = TaskSchema.dump(msg)
            
        return jsonify(retval)

    def delete(self, task_id):
        user = AuthService.current_api_user()
        if not user:
            abort(401)

        UserService(user).delete_task(task_id)
        return 'No content', 204
