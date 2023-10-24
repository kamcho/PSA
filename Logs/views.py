from django.views.generic import TemplateView

from .logging import DatabaseLogHandler  # Adjust the import path if needed

import logging
from .models import LogEntry  # Import your LogEntry model


class DatabaseLogHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def emit(self, record):
        log_entry = LogEntry(
            level=record.levelname,
            message=record.getMessage(),
            custom_field1=record.custom_field1,  # Add your custom fields here
            custom_field2=record.custom_field2,
        )
        log_entry.save()


class HLogs(TemplateView):
    template_name='Logs/logs.html'
