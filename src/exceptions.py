from typing import cast

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError

from src.core.exceptions import AppException
from src.core.schemas import ErrorDetail, ErrorResponse


def configure_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(
        _: Request,
        exc: AppException,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                code=exc.code,
                message=exc.message,
                details=[
                    ErrorDetail(
                        field=cast(str | None, d.get("field")),
                        message=cast(str, d.get("message")),
                    )
                    for d in exc.details
                ]
                if exc.details
                else None,
            ).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        details = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"][1:])
            details.append(
                ErrorDetail(
                    field=field or None,
                    message=error["msg"],
                )
            )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse(
                code="VALIDATION_ERROR",
                message="Request validation failed",
                details=details,
            ).model_dump(),
        )

    @app.exception_handler(PydanticValidationError)
    async def pydantic_validation_exception_handler(
        _: Request,
        exc: PydanticValidationError,
    ) -> JSONResponse:
        details = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            details.append(
                ErrorDetail(
                    field=field or None,
                    message=error["msg"],
                )
            )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse(
                code="VALIDATION_ERROR",
                message="Data validation failed",
                details=details,
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        _: Request,
        _exc: Exception,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                code="INTERNAL_ERROR",
                message="An unexpected error occurred",
            ).model_dump(),
        )
