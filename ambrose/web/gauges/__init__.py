from flask import Blueprint, render_template

from ambrose.models import User
from ambrose.services import AuthService, UserService
from .forms import GaugeForm

gauges_bp = Blueprint('gauges', __name__, template_folder='templates')

@gauges_bp.route('/', methods=['GET', 'POST'])
@AuthService.auth_required
def index(user: User, user_service: UserService):
    form = GaugeForm(user=user)

    if form.validate_on_submit():
        user_service.add_gauge(form.task_id.data,
                               form.min_val.data,
                               form.max_val.data,
                               form.nickname.data)

        return render_template('gauges.html', form=GaugeForm(user=user), gauges=user.gauges)

    return render_template('gauges.html', form=form, gauges=user.gauges)