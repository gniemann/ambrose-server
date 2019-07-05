import pytest

from ambrose.models import Task, LightSettings
from ambrose.services import LightService

@pytest.fixture
def light_service():
    settings = [
        LightSettings(status='succeeded', color_green=127),
        LightSettings(status='failed', color_red=127),
        LightSettings(status='inprogress', color_blue=127),
        LightSettings(status='open_prs', color_blue=127)
    ]
    return LightService(settings)

@pytest.mark.parametrize('status, expected', [
    ('Succeeded', (0, 127, 0)),
    ('Failed', (127, 0, 0)),
    ('inPROGRESS', (0, 0, 127)),
    ('open_prs', (0, 0, 127)),
])
def test_color_for_status(light_service, status, expected):
    assert light_service.color_for_status(status) == expected


@pytest.mark.parametrize('value, has_changed, expected_type', [
    ('succeeded', False, 'steady'),
    ('succeeded', True, 'initially_blinking'),
    ('inprogress', False, 'blinking'),
    ('inprogress', True, 'blinking'),
    ('failed', False, 'steady'),
    ('failed', True, 'initially_blinking'),
])
def test_light_for_task(light_service, value, has_changed, expected_type):
    task = Task(_value=value, has_changed=has_changed)
    light = light_service.light_for_task(task)
    assert light.type == expected_type
