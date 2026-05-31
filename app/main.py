from fastapi import FastAPI
from app.core.cors import setup_cors
from app.core.exception_handler import setup_exception_handler
from app.middlewares.logger_middleware import log_request_middleware
from app.routes.auth_router import router as auth_router
from app.routes.analysis_router import router as analysis_router

app = FastAPI(
    title="Compro Backend API",
    version="1.0.0",
    swagger_ui_parameters={"persistAuthorization": True},
)

setup_exception_handler(app)
setup_cors(app)
app.middleware("http")(log_request_middleware)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(analysis_router, prefix="/api/v1")
