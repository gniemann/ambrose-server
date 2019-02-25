from flask import jsonify, abort
from flask.views import MethodView
from flask_jwt_extended import jwt_required

from devops_monitor.api import TaskSchema
from devops_monitor.services import AuthService, UserService


class Tasks(MethodView):
    decorators = [jwt_required]

    def get(self, task_id):
        user = AuthService.current_api_user()
        if task_id is None:
            retval = TaskSchema().dump(user.tasks, many=True)
        else:
            msg = UserService(user).get_task(task_id)
            retval = TaskSchema.dump(msg)
            
        return jsonify(retval)

    def post(self):
        pass

    def put(self, task_id):
        pass

    def delete(self, task_id):
        user = AuthService.current_api_user()
        if not user:
            abort(401)

        UserService(user).delete_task(task_id)
        return 'No content', 204