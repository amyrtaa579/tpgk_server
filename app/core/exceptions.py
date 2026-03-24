"""Исключения приложения."""


class AppException(Exception):
    """Базовое исключение приложения."""
    
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundException(AppException):
    """Исключение для случая, когда ресурс не найден."""
    
    def __init__(self, message: str = "Ресурс не найден"):
        super().__init__(message, status_code=404)


class BadRequestException(AppException):
    """Исключение для некорректного запроса."""
    
    def __init__(self, message: str = "Некорректный запрос"):
        super().__init__(message, status_code=400)


class ValidationException(AppException):
    """Исключение для ошибок валидации."""
    
    def __init__(self, message: str = "Ошибка валидации"):
        super().__init__(message, status_code=422)
