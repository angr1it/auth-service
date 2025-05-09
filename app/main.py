from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from api import api_router
from core.startup.permissions import ensure_base_permissions
from utils.helpers.error_handling import CustomHTTPException
from config.db import db_session


async def startup_event():
    async with db_session() as session:
        await ensure_base_permissions(db=session)

app = FastAPI()

app.add_event_handler("startup", startup_event)
app.include_router(router=api_router, prefix="/api/v1")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_details = []
    for error in exc.errors():
        loc = " -> ".join([str(loc) for loc in error["loc"]])
        error_msg = f"{loc}: {error['msg']}"
        error_details.append(error_msg)

    detailed_error_msg = "; ".join(error_details)

    raise CustomHTTPException(
        error_code="ValidationError",
        description=f"Invalid input data: {detailed_error_msg}",
        status_code=400,
    )


origins = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
