from flask import Blueprint, render_template, url_for, redirect

from devops_monitor.models import User, Message
from devops_monitor.services import AuthService, UserService
from .forms import NewMessageForm, MessageForm

messages_bp = Blueprint('messages', __name__, template_folder='templates/messages')


@messages_bp.route('/', methods=['GET', 'POST'])
@AuthService.auth_required
def index(user: User):
    form = NewMessageForm()

    if form.validate_on_submit():
        return redirect(url_for('.new_message', message_type=form.type.data))

    token = AuthService.jwt(user)
    return render_template('messages.html', form=form, messages=user.messages, jwt=token)


@messages_bp.route('/new/<message_type>', methods=['GET', 'POST'])
@AuthService.auth_required
def new_message(message_type: str, user: User, user_service: UserService):
    form = MessageForm.new_message_form(message_type, user=user)

    if form.validate_on_submit():
        user_service.create_message(message_type, form.data)

        return redirect(url_for('.index'))

    params = {
        'form': form,
        'message_type': message_type,
        'message_url': url_for('.new_message', message_type=message_type),
        'is_new': True,
        'variables': Message.class_variables_for(message_type)
    }
    return render_template('message.html', **params)


@messages_bp.route('/<int:message_id>', methods=['GET', 'POST'])
@AuthService.auth_required
def edit_message(message_id: int, user: User, user_service: UserService):
    message = user_service.get_message(message_id)

    form = MessageForm.new_message_form(message.type, user=user, obj=message)
    if form.validate_on_submit():
        user_service.update_message(message, form.data)
        return redirect(url_for('.index'))

    params = {
        'form': form,
        'message_url': url_for('.edit_message', message_id=message_id),
        'is_new': False,
        'variables': message.variables
    }

    return render_template('message.html', **params)

