from flask import abort
from flask.views import MethodView
from flask_jwt_extended import jwt_required

from ambrose.services import AuthService, UserService


class Devices(MethodView):
    decorators = [jwt_required]

    def get(self):
        pass

    def delete(self, device_id):
        user = AuthService.current_api_user()
        if not user:
            abort(401)

        UserService(user).delete_device(device_id)
        return 'No content', 204

