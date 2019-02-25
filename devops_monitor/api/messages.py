from flask import abort, jsonify
from flask.views import MethodView
from flask_jwt_extended import jwt_required

from devops_monitor.api.schema import MessageSchema
from devops_monitor.services import AuthService, UserService


class Messages(MethodView):
    decorators = [jwt_required]

    def get(self, message_id):
        user = AuthService.current_api_user()
        if message_id is None:
            retval = MessageSchema().dump(user.messages, many=True)
        else:
            msg = UserService(user).get_message(message_id)
            retval = MessageSchema.dump(msg)
        return jsonify(retval)

    def post(self):
        pass

    def put(self, message_id):
        pass

    def delete(self, message_id):
        user = AuthService.current_api_user()
        if not user:
            abort(401)

        UserService(user).delete_message(message_id)
        return 'No content', 204