# app/schemas/question_schema.py
from flask import jsonify
from marshmallow import Schema, fields, validate, ValidationError

class QuestionSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1))
    type = fields.Str(required=True, validate=validate.OneOf(["single", "multiply", "text"]))
    order = fields.Integer(required=False, default=0)
    required = fields.Bool(required=False, default=False)


    def handle_error(self, exc, data, **kwargs):
        raise ValidationError(exc.messages)

    @staticmethod
    def validate_create(data):
        schema = QuestionSchema()
        errors = schema.validate(data)
        if errors:
            raise ValidationError(errors)
        if not data.get('title'):
            raise ValidationError({"title": ["Missing data for required field."]})
        if not data.get('type'):
            raise ValidationError({"type": ["Missing data for required field."]})
        return data


    @staticmethod
    def validate_update(data):
        schema = QuestionSchema()
        errors = schema.validate(data)
        if errors:
            raise ValidationError(errors)
        if not data.get('text'):
            raise ValidationError({"text": ["Missing data for required field."]})
        if not data.get('type'):
            raise ValidationError({"type": ["Missing data for required field."]})
        return data
