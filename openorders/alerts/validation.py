from marshmallow import Schema, fields

class EmailSchema(Schema):
    email = fields.Email(required=True)