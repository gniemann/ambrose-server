import os

from flask import Blueprint, jsonify

from devops import DevOpsService, Credentials

api_bp = Blueprint('api', __name__)

ORGANIZATION = 'mobilecfa'
PROJECT = 'LidlAPI'

@api_bp.route('/status/releases')
def get_status():
    username = os.getenv('DEVOPS_USERNAME')
    token = os.getenv('DEVOPS_TOKEN')

    service = DevOpsService(Credentials(username, token))
    summary = service.get_release_summary(ORGANIZATION, PROJECT, 5)

    retVal = [
        summary['Development'],
        summary['Integration'],
        summary['QA'],
        summary['Production']
    ]

    return jsonify(retVal)

