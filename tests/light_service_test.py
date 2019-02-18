import pytest

from devops_monitor.models import Task
from devops_monitor.services import LightService

@pytest.mark.parametrize('status, expected', [
    ('Succeeded', (0, 255, 0)),
    ('Failed', (255, 0, 0)),
    ('Queued', (0, 0, 255)),
    ('in_PROGRESS', (0, 0, 255)),
    ('Pending_Approval', (255, 0, 255))
])
def test_color_for_status(status, expected):
    assert LightService.color_for_status(status) == expected


@pytest.mark.parametrize('status, has_changed, expected_type', [
    ('succeeded', False, 'steady'),
    ('succeeded', True, 'initially_blinking'),
    ('queued', False, 'blinking'),
    ('queued', True, 'blinking'),
    ('in_progress', False, 'blinking'),
    ('in_progress', True, 'blinking'),
    ('pending_approval', False, 'blinking'),
    ('pending_approval', True, 'blinking'),
    ('failed', False, 'steady'),
    ('failed', True, 'initially_blinking')
])
def test_light_for_task(status, has_changed, expected_type):
    task = Task(_status=status, has_changed=has_changed)
    light = LightService.light_for_task(task)
    assert light.type == expected_type
