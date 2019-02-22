from flask import Blueprint, render_template, url_for, redirect

from devops_monitor.services import AuthService
from devops_monitor.web.forms import NewMessageForm, MessageForm

messages_bp = Blueprint('messages', __name__, template_folder='templates/messages')


@messages_bp.route('/', methods=['GET', 'POST'])
@AuthService.auth_required
def index(user):
    form = NewMessageForm()

    if form.validate_on_submit():
        return redirect(url_for('.new_message', message_type=form.type.data))

    return render_template('messages.html', form=form, messages=user.messages)


@messages_bp.route('/new/<message_type>', methods=['GET', 'POST'])
@AuthService.auth_required
def new_message(message_type, user, user_service):
    form = MessageForm.new_message_form(message_type, user=user)

    if form.validate_on_submit():
        user_service.create_message(message_type, form.data)

        return redirect(url_for('.index'))

    return render_template('message.html', form=form, message_type=message_type,
                           message_url=url_for('.new_message', message_type=message_type), is_new=True)


@messages_bp.route('/<int:message_id>', methods=['GET', 'POST'])
@AuthService.auth_required
def edit_message(message_id, user, user_service):
    message = user_service.get_message(message_id)

    form = MessageForm.new_message_form(message.type, user=user, obj=message)
    if form.validate_on_submit():
        user_service.update_message(message, form.data)
        return redirect(url_for('.index'))

    return render_template('message.html', form=form, message_type='datetime',
                           message_url=url_for('.edit_message', message_id=message_id), is_new=False)

