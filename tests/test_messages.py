import pytest

from devops_monitor.models import DateTimeMessage


def test_datetime_message_task():
    task = DateTimeMessage(text='Current time is {}', dateformat='%b %m, %M%M')

    assert 'Current time is' in task.value