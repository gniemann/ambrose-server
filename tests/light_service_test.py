import pytest

from devops_monitor.models import Task
from devops_monitor.services import LightService

@pytest.mark.parametrize('status, expected', [
    ('Succeeded', (0, 255, 0)),
    ('Failed', (255, 0, 0)),
    ('Queued', (0, 0, 255)),
    ('inPROGRESS', (0, 0, 255)),
    ('Pending_Approval', (255, 0, 255))
])
def test_color_for_status(status, expected):
    assert LightService.color_for_status(status) == expected


@pytest.mark.parametrize('value, prev_value, expected_type', [
    ('succeeded', 'succeeded', 'steady'),
    ('succeeded', 'failed', 'initially_blinking'),
    ('queued', 'queued', 'blinking'),
    ('queued', 'failed', 'blinking'),
    ('inprogress', 'inprogress', 'blinking'),
    ('inprogress', 'failed', 'blinking'),
    ('pending_approval', 'pending_approval', 'blinking'),
    ('pending_approval', 'failed', 'blinking'),
    ('failed', 'failed', 'steady'),
    ('failed', 'inprogress', 'initially_blinking')
])
def test_light_for_task(value, prev_value, expected_type):
    task = Task(_value=value, _prev_value=prev_value)
    light = LightService.light_for_task(task)
    assert light.type == expected_type
