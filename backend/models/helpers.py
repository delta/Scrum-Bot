# Helpers to help with data validation
from mongoengine import ValidationError


def notEmpty(val):
    if not val:
        raise ValidationError("Field cannot be empty")
