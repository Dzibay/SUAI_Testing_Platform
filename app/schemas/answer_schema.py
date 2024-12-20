# app/schemas/answer_schema.py

from marshmallow import Schema, fields, validate, ValidationError

class AnswerSchema(Schema):
    text = fields.Str(required=True, validate=validate.Length(min=1))
    is_correct = fields.Bool(required=False)

    def handle_error(self, exc, data, **kwargs):
        """Log and raise a validation error."""
        raise ValidationError(exc.messages)

    @staticmethod
    def validate_create(data):
        schema = AnswerSchema()
        errors = schema.validate(data)
        if errors:
            raise ValidationError(errors)
        if not data.get('text'):
            raise ValidationError({"text": ["Missing data for required field."]})
        return data

    @staticmethod
    def validate_update(data):
        schema = AnswerSchema()
        errors = schema.validate(data)
        if errors:
            raise ValidationError(errors)
        if not data.get('text'):
            raise ValidationError({"text": ["Missing data for required field."]})
        return data
