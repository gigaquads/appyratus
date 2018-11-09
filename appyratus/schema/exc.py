class ValidationError(Exception):
    def __init__(self, schema: 'Schema', errors: dict):
        super().__init__()
        self.schema = schema
        self.errors = errors
