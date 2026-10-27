class ApplicationError(Exception): pass
class ConfigurationError(ApplicationError): pass
class DataError(ApplicationError): pass
class DataImportError(DataError): pass
class DataExportError(DataError): pass
class RecordValidationError(DataError):
    def __init__(self, message: str, *, line_number: int | None = None, field: str | None = None):
        super().__init__(message)
        self.line_number = line_number
        self.field = field
