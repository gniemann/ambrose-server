from collections import namedtuple
from typing import List

from ambrose.models import User, Task

Color = namedtuple('Color', 'red green blue')

RED = Color(255, 0, 0)
GREEN = Color(0, 255, 0)
BLUE = Color(0, 0, 255)
MAGENTA = Color(255, 0, 255)
OFF = Color(0, 0, 0)


class LightConfiguration:
    def __init__(self, type: str = 'undefined', primary_color: Color = OFF):
        self.primary_color = primary_color
        self.type = type


class SteadyLight(LightConfiguration):
    def __init__(self, primary_color: Color):
        super(SteadyLight, self).__init__('steady', primary_color)


class BlinkingLight(LightConfiguration):
    def __init__(self, primary_color: Color, primary_period: int, secondary_color: Color, secondary_period: int):
        super(BlinkingLight, self).__init__('blinking', primary_color)
        self.primary_period = primary_period
        self.secondary_color = secondary_color
        self.secondary_period = secondary_period


class InitiallyBlinking(LightConfiguration):
    def __init__(self, primary_color: Color, primary_period: int, secondary_period: int, repeat: int):
        super(InitiallyBlinking, self).__init__('initially_blinking', primary_color)
        self.primary_color = primary_color
        self.primary_period = primary_period
        self.secondary_period = secondary_period
        self.repeat = repeat
        self.secondary_color = OFF


class LightService:
    @classmethod
    def color_for_status(cls, status: str) -> Color:
        if status is None:
            return OFF

        status = status.lower()
        if status == 'succeeded':
            return GREEN
        elif status == 'failed' or status == 'canceled':
            return RED
        elif status == 'queued' or status == 'inprogress':
            return BLUE
        elif status == 'pending_approval':
            return MAGENTA
        elif status == 'no_open_prs':
            return GREEN
        elif status == 'prs_with_issues':
            return RED
        elif status == 'open_prs':
            return BLUE
        elif status == 'prs_need_review':
            return BLUE
        else:
            return OFF

    @classmethod
    def light_for_task(cls, task: Task) -> LightConfiguration:
        if task is None:
            return SteadyLight(OFF)

        status = task.value.lower()
        primary_color = cls.color_for_status(status)

        # queued, in_progress and pending_approval always are the same regardless of has_changed (to ensure they persist between updates
        if status == 'queued' or \
                status == 'inprogress':
            secondary_color = cls.color_for_status(task.prev_value)
            if secondary_color == primary_color:
                secondary_color = OFF
            return BlinkingLight(primary_color, 4, secondary_color, 4)

        # all others are different based on has_changed
        if not task.has_changed:
            return SteadyLight(primary_color)

        primary_period = 2 if status == 'succeeded' else 1

        return InitiallyBlinking(primary_color, primary_period, 1, 20)

    @classmethod
    def lights_for_user(cls, user: User) -> List[LightConfiguration]:
        return [cls.light_for_task(light.task) for light in user.lights]