import logging

class DatabaseLogHandler(logging.Handler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def emit(self, record):
        from .models import LogEntry  # Import your LogEntry model

        try:

            # Extract fields from the log record
            url = getattr(record, 'url', None)
            app_name = getattr(record, 'app_name', None)
            school = getattr(record, 'school', None)
            level = record.levelname
            error_type = getattr(record, 'error_type', None)
            message = record.getMessage()
            user = getattr(record, 'user', None)
            model = getattr(record, 'model', None)
            object_id = getattr(record, 'object_id', None)

            # Create a LogEntry instance with the extracted fields
            log_entry = LogEntry(
                app_name=app_name,
                url=url,
                school=school,
                level=level,
                error_type=error_type,
                message=message,
                user=user,
                model=model,
                object_id=object_id,
            )

            log_entry.save()

        except Exception as e:
            pass  # Handle exceptions if needed

# In your views or wherever you're logging an error, you can now pass the custom fields as kwargs


