# app/schemas/test_schema.py

from marshmallow import Schema, fields, validate, ValidationError

class UserInputSchema(Schema):
    type = fields.Str(required=True, validate=validate.OneOf(["text", "email", "password", "textarea"]))
    isRequired = fields.Bool(required=True)
    default = fields.Str(required=False)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=128))

class TestSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=128))
    description = fields.Str(required=False)
    password = fields.Str(required=False)
    complete_time = fields.Dict(required=False)
    user_inputs = fields.List(fields.Nested(UserInputSchema), required=False)
    type = fields.Str(required=True, validate=validate.OneOf(["test", "survey"]))
    options = fields.Dict(required=False)
    end_date = fields.DateTime(required=False)
    start_date = fields.DateTime(required=False)

    def handle_error(self, exc, data, **kwargs):
        """Log and raise a validation error."""
        raise ValidationError(exc.messages)



    @staticmethod
    def validate_create(data):
        schema = TestSchema()
        errors = schema.validate(data)
        if errors:
            raise ValidationError(errors)

        TestSchema._validate_required_fields(data, is_create=True)
        return data

    @staticmethod
    def validate_update(data):
        schema = TestSchema(partial=True)  # Allow partial updates
        errors = schema.validate(data)
        if errors:
            raise ValidationError(errors)

        # Ensure 'type' is not being updated
        if 'type' in data:
            raise ValidationError({"type": ["Field cannot be updated."]})

        TestSchema._validate_required_fields(data, is_create=False)
        return data

    @staticmethod
    def _validate_required_fields(data, is_create):
        if is_create and not data.get('type'):
            raise ValidationError({"type": ["Missing data for required field."]})
        if not data.get('title'):
            raise ValidationError({"title": ["Missing data for required field."]})
        if data.get('options'):
            if data['options'].get('description') and not data.get('description'):
                raise ValidationError({"description": ["Missing data for required field."]})
            if data['options'].get('user_inputs') and not data.get('user_inputs'):
                raise ValidationError({"user_inputs": ["Missing data for required field."]})
            if data['options'].get('password') and not data.get('password'):
                raise ValidationError({"password": ["Missing data for required field."]})
            if data['options'].get('complete_time') and not data.get('complete_time'):
                raise ValidationError({"complete_time": ["Missing data for required field."]})
