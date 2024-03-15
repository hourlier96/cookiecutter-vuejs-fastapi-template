import contextvars
import logging
import sys
from typing import Any, no_type_check

from fastapi.logger import logger as fastapi_logger
from google.cloud.logging_v2.client import Client as google_cloud_logging_v2_client
from google.cloud.logging_v2.handlers import CloudLoggingFilter, CloudLoggingHandler
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import settings

cloud_trace_context: contextvars.ContextVar = contextvars.ContextVar(
    "cloud_trace_context", default=""
)
http_request_context: contextvars.ContextVar = contextvars.ContextVar(
    "http_request_context", default=dict({})
)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to grab the trace context from the incoming request and store it in the contextvars.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if "x-cloud-trace-context" in request.headers:
            cloud_trace_context.set(request.headers.get("x-cloud-trace-context"))

        http_request = {
            "requestMethod": request.method,
            "requestUrl": request.url.path,
            "requestSize": sys.getsizeof(request),
            "remoteIp": request.client.host if request.client else None,
            "protocol": request.url.scheme,
        }

        if "referrer" in request.headers:
            http_request["referrer"] = request.headers.get("referrer")

        if "user-agent" in request.headers:
            http_request["userAgent"] = request.headers.get("user-agent")

        http_request_context.set(http_request)

        try:
            return await call_next(request)
        except Exception as ex:
            logging.exception(f"Request failed: {ex}")
            return JSONResponse(status_code=500, content={"success": False, "message": str(ex)})


class GoogleCloudLogFilter(CloudLoggingFilter):
    @no_type_check
    def filter(self, record: logging.LogRecord) -> bool:
        """Filter out all log records to group them by trace context."""
        try:
            record.http_request = http_request_context.get()

            trace_header = cloud_trace_context.get()
            if trace_header:
                # Exemple trace_header: "382d4f4c6b7bb2f4a972559d9085001d/1;o=1"
                # with format: "TRACE_ID/SPAN_ID;o=TRACE_TRUE"
                trace_span, trace_true = trace_header.split(";o=")

                # trace_true defines if the request should be traced
                if int(trace_true):
                    trace_id, span_id = trace_span.split("/")
                    record.trace = f"projects/{self.project}/traces/{trace_id}"
                    record.span_id = span_id

        except Exception:
            pass

        super().filter(record)

        return True


class Logging:
    def __init__(
        self,
        name: str = settings.LOG_NAME,
        level: int = settings.LOG_LEVEL,
    ) -> None:
        self.logger = fastapi_logger
        self.name = name
        self.level = level

    def init_cloud_logger(self) -> None:
        gcloud_logging_client = google_cloud_logging_v2_client()
        gcloud_logging_handler = CloudLoggingHandler(gcloud_logging_client, name=self.name)
        gcloud_logging_filter = GoogleCloudLogFilter(project=gcloud_logging_client.project)

        self.logger.addFilter(gcloud_logging_filter)
        self.logger.addHandler(gcloud_logging_handler)

    def get_logger(self) -> logging.Logger:
        """
        If running in local, attach a "console handler" to set our log_level
        If running in another env (GAE or GCR), initialize the Cloud Logger.
        """
        if settings.ENV.lower() in ["local", "test"]:
            local_handler = logging.StreamHandler()
            self.logger.addHandler(local_handler)
        else:
            self.init_cloud_logger()

        # Force local and cloud handlers to use the same LOG_LEVEL as FastAPI's
        for handler in self.logger.handlers:
            handler.setLevel(level=self.level)
            formatter = logging.Formatter(
                fmt="[%(asctime)s] - [%(pathname)s] -  [%(levelname)s] - %(message)s"
            )
            handler.setFormatter(formatter)

        return self.logger


class Singleton(type):
    _instances: dict = {}

    def __call__(cls, *args, **kwargs) -> Any:  # type: ignore
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class LoggerStruct(metaclass=Singleton):
    def __init__(self) -> None:
        # Log struct is only available in production, so we need to mock it
        self._logger_struct = type("obj", (object,), {"log_struct": lambda x: None})
        if settings.ENV not in ["local", "test"]:
            gcloud_logging_client = google_cloud_logging_v2_client()
            # Log struct is meant to make easier to query logs in production
            self._logger_struct = gcloud_logging_client.logger(settings.LOG_NAME)

    @property
    def logger_struct(self) -> Any:
        return self._logger_struct


# Update the "fastapi" logger to have a _global_ level of `settings.LOG_LEVEL`
logging.getLogger("fastapi").setLevel(settings.LOG_LEVEL)
log: logging.Logger = Logging().get_logger()
logger_struct = LoggerStruct().logger_struct
