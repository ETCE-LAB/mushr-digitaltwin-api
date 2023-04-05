from django.db import models
from django.core.exceptions import ValidationError

class ISO8601Converter:
    """Convert ISO8601 formatted string to python datetime.datetime

    """
    regex = '[^/]+'

    def to_python(self, value):
        try:
            return(models.DateTimeField().to_python(value))
        except ValidationError as E:
            raise ValueError(E)

    def to_url(self, value):
        try:
            return(value.isoformat())
        except Exception as E:
            raise ValueError
