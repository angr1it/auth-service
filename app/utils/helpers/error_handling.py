from typing import Optional, Any

from fastapi import HTTPException


class CustomHTTPException(HTTPException):
    def __init__(
        self,
        error_code: str,
        description: str,
        status_code: int = 400,
        data: Optional[Any] = None,
    ):
        self.error_code = error_code
        self.description = description
        self.data = data
        super().__init__(status_code=status_code, detail=description)
