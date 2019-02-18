from collections import namedtuple

Color = namedtuple('Color', 'red green blue')

RED = Color(255, 0, 0)
GREEN = Color(0, 255, 0)
BLUE = Color(0, 0, 255)
MAGENTA = Color(255, 0, 255)
OFF = Color(0, 0, 0)


class LightConfiguration:
    def __init__(self, type='undefined', primary_color=OFF):
        self.primary_color = primary_color
        self.type = type


class SteadyLight(LightConfiguration):
    def __init__(self, primary_color):
        super(SteadyLight, self).__init__('steady', primary_color)


class BlinkingLight(LightConfiguration):
    def __init__(self, primary_color, primary_period, secondary_color, secondary_period):
        super(BlinkingLight, self).__init__('blinking', primary_color)
        self.primary_period = primary_period
        self.secondary_color = secondary_color
        self.secondary_period = secondary_period


class InitiallyBlinking(LightConfiguration):
    def __init__(self, primary_color, primary_period, secondary_period, repeat):
        super(InitiallyBlinking, self).__init__('initially_blinking', primary_color)
        self.primary_color = primary_color
        self.primary_period = primary_period
        self.secondary_period = secondary_period
        self.repeat = repeat
        self.secondary_color = OFF


class LightService:
    @classmethod
    def color_for_status(cls, status):
        if status is None:
            return OFF

        status = status.lower()
        if status == 'succeeded':
            return GREEN
        elif status == 'failed':
            return RED
        elif status == 'queued' or status == 'in_progress':
            return BLUE
        elif status == 'pending_approval':
            return MAGENTA
        else:
            return OFF

    @classmethod
    def light_for_task(cls, task):
        if task is None:
            return SteadyLight(OFF)

        status = task.status.lower()
        primary_color = cls.color_for_status(status)

        # queued, in_progress and pending_approval always are the same regardless of has_changed (to ensure they persist between updates
        if status == 'queued' or status == 'in_progress' or status == 'pending_approval':
            secondary_color = cls.color_for_status(task.prev_status)
            return BlinkingLight(primary_color, 4, secondary_color, 4)

        # all others are different based on has_changed
        if not task.has_changed:
            return SteadyLight(primary_color)

        primary_period = 2 if status == 'succeeded' else 1

        return InitiallyBlinking(primary_color, primary_period, 1, 20)

    @classmethod
    def lights_for_user(cls, user):
        return [cls.light_for_task(light.task) for light in user.lights]