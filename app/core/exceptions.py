from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class OrderManagementException(Exception):
    def __init__(self, detail: str, status_code: int = 400):
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)
