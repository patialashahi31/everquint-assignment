from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


# ── Custom exception classes ─────────────────────────────

class NotFoundError(Exception):
    def __init__(self, message: str):
        self.message = message


class ConflictError(Exception):
    def __init__(self, message: str):
        self.message = message


class ValidationError(Exception):
    def __init__(self, message: str):
        self.message = message


# ── Handler registration ─────────────────────────────────

def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        return JSONResponse(
            status_code=404,
            content={"error": "NotFoundError", "message": exc.message},
        )

    @app.exception_handler(ConflictError)
    async def conflict_handler(request: Request, exc: ConflictError):
        return JSONResponse(
            status_code=409,
            content={"error": "ConflictError", "message": exc.message},
        )

    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=400,
            content={"error": "ValidationError", "message": exc.message},
        )

    @app.exception_handler(RequestValidationError)
    async def pydantic_validation_handler(request: Request, exc: RequestValidationError):
        # Flatten pydantic errors into a single readable message
        errors = exc.errors()
        message = "; ".join(
            f"{' -> '.join(str(l) for l in e['loc'])}: {e['msg']}"
            for e in errors
        )
        return JSONResponse(
            status_code=400,
            content={"error": "ValidationError", "message": message},
        )

    @app.exception_handler(Exception)
    async def generic_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"error": "InternalServerError", "message": "An unexpected error occurred"},
        )