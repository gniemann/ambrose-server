import functools
from collections import abc
from typing import Union, Type, Callable

from flask import jsonify
from marshmallow import Schema, fields


class ColorSchema(Schema):
    red = fields.Integer()
    green = fields.Integer()
    blue = fields.Integer()


class LightSchema(Schema):
    type = fields.String()
    primary_color = fields.Nested(ColorSchema)
    primary_period = fields.Integer(missing=None)
    secondary_color = fields.Nested(ColorSchema, missing=None)
    secondary_period = fields.Integer(missing=None)
    repeat = fields.Integer(missing=None)


class GaugeSchema(Schema):
    position = fields.Float()

class StatusSchema(Schema):
    lights = fields.Nested(LightSchema, many=True)
    messages = fields.List(fields.String())
    gauges = fields.Nested(GaugeSchema, many=True)


class MessageSchema(Schema):
    id = fields.Integer()
    type = fields.String()
    value = fields.String()
    text = fields.String()


class LoginSchema(Schema):
    username = fields.String()
    password = fields.String()


class AccessTokenSchema(Schema):
    access_token = fields.String()


class TaskSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    value = fields.String()
    prev_value = fields.String()
    has_changed = fields.Boolean()


def with_schema(schema: Union[Type[Schema], Schema]) -> Callable[[Callable], Callable]:
    def decorator(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            retval = func(*args, **kwargs)

            many = isinstance(retval, abc.MutableSequence)
            if not isinstance(schema, Schema):
                converter = schema()
            else:
                converter = schema

            return jsonify(converter.dump(retval, many=many))

        return inner

    return decorator
