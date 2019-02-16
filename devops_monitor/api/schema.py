import functools
from collections import abc

from flask import jsonify
from marshmallow import Schema, fields


class TaskSchema(Schema):
    name = fields.String()
    status = fields.String()
    has_changed = fields.Boolean()


class StatusSchema(Schema):
    tasks = fields.Nested(TaskSchema, many=True)
    messages = fields.List(fields.String())


def with_schema(schema):
    def decorator(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            retval = func(*args, **kwargs)

            if not isinstance(schema, Schema):
                many = isinstance(retval, abc.MutableSequence)
                converter = schema(many=many)
            else:
                converter = schema

            return jsonify(converter.dump(retval))

        return inner

    return decorator