import pytest

from devops_monitor.models import DateTimeMessage, TextMessage, TaskMessage, RandomMessage


def test_datetime_message_task():
    task = DateTimeMessage(text='Current time is {datetime}', dateformat='%b %m, %M%M')

    assert 'Current time is' in task.value


@pytest.mark.parametrize('task_class, expected', [
    (TextMessage, 'text'),
    (DateTimeMessage, 'datetime'),
    (TaskMessage, 'task')
])
def test_message_type(task_class, expected):
    task = task_class()
    assert task.type == expected


def test_random_message():
    message = RandomMessage(text='{message}')
    message.messages.append('a')

    assert message.value == 'a'
