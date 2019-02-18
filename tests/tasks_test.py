import pytest

from devops_monitor.models import DateTimeMessageTask


def test_datetime_message_task():
    task = DateTimeMessageTask(format='Current time is {}', dateformat='%b %m, %M%M')

    date_str = task.message

    assert 'Current time is' in date_str