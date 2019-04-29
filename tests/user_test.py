import random
import string

import pytest

import ambrose
from ambrose.models import Task


@pytest.fixture(scope='module')
def randomize():
    random.seed()


@pytest.mark.usefixtures('randomize')
def test_resize_lights(user):
    for size in [random.randint(0, 20) for _ in range(100)]:
        user.resize_lights(size)
        ambrose.db.session.commit()

        assert len(user.lights) == size
        for idx, light in enumerate(user.lights):
            assert light.slot == idx + 1


@pytest.mark.usefixtures('randomize')
def test_set_task_for_light(user):
    for slot in {random.randint(0, 50) for _ in range(10)}:
        value = ''.join(random.sample(string.ascii_letters, 10))
        task = Task(_value=value)
        user.set_task_for_light(task, slot)

        assert user.light_for_slot(slot).task.value == value