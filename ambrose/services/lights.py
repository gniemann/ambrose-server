from collections import namedtuple
from typing import List

from ambrose.models import Task, Device, LightSettings

Color = namedtuple('Color', 'red green blue')

RED = Color(255, 0, 0)
GREEN = Color(0, 255, 0)
BLUE = Color(0, 0, 255)
MAGENTA = Color(255, 0, 255)
OFF = Color(0, 0, 0)
YELLOW = Color(255, 255, 0)


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
    def __init__(self, settings: List[LightSettings]):
        self.settings = settings

    def color_for_status(self, status: str) -> Color:
        if status is None:
            return OFF

        status = status.lower()

        for setting in self.settings:
            if status == setting.status.lower():
                return Color(setting.color_red, setting.color_green, setting.color_blue)

        return OFF

    def light_for_task(self, task: Task) -> LightConfiguration:
        if task is None or task.value is None:
            return SteadyLight(OFF)

        status = task.value.lower()
        primary_color = self.color_for_status(status)

        # queued, in_progress and pending_approval always are the same regardless of has_changed (to ensure they persist between updates
        if status == 'queued' or \
                status == 'inprogress':
            secondary_color = self.color_for_status(task.prev_value)
            if secondary_color == primary_color:
                secondary_color = OFF
            return BlinkingLight(primary_color, 4, secondary_color, 4)

        # all others are different based on has_changed
        if not task.has_changed:
            return SteadyLight(primary_color)

        primary_period = 2 if status == 'succeeded' else 1

        return InitiallyBlinking(primary_color, primary_period, 1, 20)

    def lights_for_device(self, device: Device) -> List[LightConfiguration]:
        return [self.light_for_task(light.task) for light in device.lights]