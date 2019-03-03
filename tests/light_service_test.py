import pytest

from devops_monitor.models import Task
from devops_monitor.services import LightService

@pytest.mark.parametrize('status, expected', [
    ('Succeeded', (0, 255, 0)),
    ('Failed', (255, 0, 0)),
    ('Queued', (0, 0, 255)),
    ('inPROGRESS', (0, 0, 255)),
    ('Pending_Approval', (255, 0, 255)),
    ('prs_need_review', (0, 0, 255)),
    ('prs_with_issues', (255, 0, 0)),
    ('open_prs', (0, 0, 255)),
    ('no_open_prs', (0, 255, 0))
])
def test_color_for_status(status, expected):
    assert LightService.color_for_status(status) == expected


@pytest.mark.parametrize('value, has_changed, expected_type', [
    ('succeeded', False, 'steady'),
    ('succeeded', True, 'initially_blinking'),
    ('queued', False, 'blinking'),
    ('queued', True, 'blinking'),
    ('inprogress', False, 'blinking'),
    ('inprogress', True, 'blinking'),
    ('pending_approval', False, 'blinking'),
    ('pending_approval', True, 'blinking'),
    ('failed', False, 'steady'),
    ('failed', True, 'initially_blinking'),
    ('prs_need_review', True, 'blinking'),
    ('prs_need_review', False, 'blinking')
])
def test_light_for_task(value, has_changed, expected_type):
    task = Task(_value=value, has_changed=has_changed)
    light = LightService.light_for_task(task)
    assert light.type == expected_type
