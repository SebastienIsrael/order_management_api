from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class OrderManagementException(Exception):
    """Base class for expected application errors."""

    status_code = 400

    def __init__(self, detail: str, status_code: int | None = None) -> None:
        self.detail = detail
        if status_code is not None:
            self.status_code = status_code
        super().__init__(detail)


class BadRequestError(OrderManagementException):
    status_code = 400


class NotFoundError(OrderManagementException):
    status_code = 404


class ConflictError(OrderManagementException):
    status_code = 409


class UnprocessableEntityError(OrderManagementException):
    status_code = 422


async def _order_management_exception_handler(
    _request: Request, exc: OrderManagementException
) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        OrderManagementException,
        _order_management_exception_handler,
    )
