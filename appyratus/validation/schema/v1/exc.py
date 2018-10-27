from appyratus.exc import AppyratusError


class ValidationError(AppyratusError):
    def __init__(self, reasons: dict=None):
        self.reasons = reasons or {}
        super().__init__(str(self.reasons))
