from typing import Any, Optional


class ResponseBuilder:
    @staticmethod
    def success(message: str = "Success", data: Optional[Any] = None):
        return {
            "status": True,
            "message": message,
            "data": data,
            "errors": None,
        }

    @staticmethod
    def error(message: str = "Something went wrong", errors: Optional[Any] = None):
        return {
            "status": False,
            "message": message,
            "data": None,
            "errors": errors,
        }
