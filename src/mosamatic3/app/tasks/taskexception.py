class TaskException(Exception):
    def __init__(self, message: str, error_code: int=None) -> None:
        super(TaskException, self).__init__(message)
        self.error_code = error_code

    def __str__(self) -> str:
        if self.error_code:
            return f'{self.args[0]} (Error code: {self.error_code})'
        return self.args[0]