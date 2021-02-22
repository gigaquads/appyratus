class ValidationError(Exception):
    def __init__(self, schema: 'Schema', errors: dict):
        super().__init__(str(errors))
        self.schema = schema
        self.errors = errors
