import inspect
import json
import time
# from app.api.deps import raise_401
# import jwt
from typing import Any
# from fastapi.security import HTTPAuthorizationCredentials, OAuth2PasswordBearer

import uvicorn
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from pydantic import ValidationError
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse
from starlette.types import Message
from starlette_context import context
from starlette_context.middleware import RawContextMiddleware
from typing_extensions import AsyncIterator

from app.api.router import api_router
from app.core.cloud_logging import LoggingMiddleware, log, logger_struct
from app.core.config import settings

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> StreamingResponse:
        try:
            if inspect.iscoroutinefunction(call_next):
                response = await call_next(request)
            else:
                response = call_next(request)  # type: ignore
        except ValidationError as e:
            log.warning(e)
            response = JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": e.errors()}
            )
        except ValueError as e:
            log.warning(e)
            response = JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "detail": [{"msg": str(e), "loc": request.url.path, "type": "Value error"}]
                },
            )
        except Exception as e:
            log.warning(e)
            status_ = getattr(e, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR)
            response = JSONResponse(
                status_code=status_,
                content={"detail": [{"msg": str(e), "loc": request.url.path, "type": "Unknown"}]},
            )
        return response  # type: ignore


# class JwtAccessMiddleware(BaseHTTPMiddleware):
#     """JWT Access Middleware"""

#     async def dispatch(
#         self, request: Request, call_next: RequestResponseEndpoint
#     ) -> StreamingResponse:
#         cred: HTTPAuthorizationCredentials | None = await oauth2_scheme(
#             request
#         )  # TODO your own or Fastapi One
#         if cred:
#             context["USER_ID"] = self.verify_token(cred.credentials)
#         if inspect.iscoroutinefunction(call_next):
#             response = await call_next(request)
#         else:
#             response = call_next(request)  # type: ignore
#         return response  # type: ignore

#     def verify_token(self, creds):
#         # Verify JWT header
#         try:
#             jwt_decoded = jwt.decode(creds)
#         except Exception:
#             log.exception("Invalid JWT")
#             raise_401()
#         return jwt_decoded


class LoggingMiddlewareReq(BaseHTTPMiddleware):
    """In order to get the body request and the body respone, and all the information about the request
    We have build this middleware.
    It will log all the information about the request and the response
    """

    def __init__(self, app: FastAPI):
        super().__init__(app)

    async def set_body(self, request: Request, body: bytes) -> None:
        """Issue with starlette : https://github.com/encode/starlette/issues/847
        Need to override the receive method to get the body of the request, otherwise it will hang
        """

        async def receive() -> Message:
            return {"type": "http.request", "body": body}

        request._receive = receive

    async def get_body(self, request: Request) -> bytes:
        """Workaround for hang issue"""
        body = await request.body()
        await self.set_body(request, body)
        return body

    async def read_bytes(self, generator: AsyncIterator[bytes]) -> bytes:
        body = b""
        async for data in generator:
            body += data
        return body

    async def resolve_response(self, streaming_response: Any) -> Response:
        """Resolve the response from the streaming response"""
        content = await self.read_bytes(streaming_response.body_iterator)
        status_code = streaming_response.status_code
        headers = dict(streaming_response.headers) if streaming_response.headers else None
        media_type = "application/json"
        background = streaming_response.background
        return Response(content, status_code, headers, media_type, background)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Any:
        try:
            request_body = None
            try:
                request_body = json.loads(await request.body())
            except Exception:
                pass
            response = await call_next(request)
            response_body = await self.resolve_response(response)
            if settings.ENV in ["local", "test"]:
                self.log_request(request, request_body, context)
                self.log_response(request, response_body)
            logger_struct.log_struct(
                {
                    "user": context.get("USER_ID"),
                    "method": request.method,
                    "path": request.url.path,
                    "path_params": request.path_params,
                    "query": request.query_params._dict,
                    "body": request_body if request_body else {},
                    "status_code": response_body.status_code,
                    "content": response_body.body.decode("utf-8"),
                }
            )
        except Exception as e:
            log.error("Error in logging middleware")
            log.error(e)
        finally:
            return response_body if response_body else response

    def log_request(self, request, request_body, context):
        header = f"\n===== REQUEST ({request.method} {request.url.path}) =====\n"
        print(header)

        print("   Author:")
        if context.get("USER_ID"):
            print(f"      f{context.get('USER_ID')}")
        else:
            print("      Unknown")

        print("\n   Query parameters:")
        if request.query_params._dict and len(request.query_params._dict) > 0:
            for key, value in request.query_params._dict.items():
                print(f"      {key}: {value}")
        else:
            print("      Empty")
        print("\n   Path parameters:")
        if request.path_params and len(request.path_params) > 0:
            for key, value in request.path_params.items():
                print(f"      {key}: {value}")
        else:
            print("      Empty")
        print("\n   Body:")
        if request_body and len(request_body) > 0:
            for key, value in request_body.items():
                print(f"      {key}: {value}")
        else:
            print("      Empty")

    def log_response(self, request, response_body):
        header = f"\n\n===== RESPONSE ({request.method} {request.url.path}) =====\n"
        print(header)
        if response_body:
            content = json.loads(response_body.body.decode("utf-8"))
            print("   Status code:")
            print(f"      {response_body.status_code}")
            print("\n   Content-Length:")
            print(f"      {len(str(content))}")
            print("\n   Content:")
            if "total" in content:
                print(f"      {content['total']} items")
            elif isinstance(content, list):
                print(f"      {len(content)} items")
            else:
                print(f"      {content}")

        print(("\n" + "".join(["=" for _ in header]) + "\n")[0:100])


class MetricMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> StreamingResponse:
        start = time.perf_counter()
        if inspect.iscoroutinefunction(call_next):
            response = await call_next(request)
        else:
            response = call_next(request)  # type: ignore
        end_time = time.perf_counter() - start
        log.info(f"Request time {end_time:.3f} seconds")
        response.headers["X-Request-Time"] = f"{end_time:.3f}"
        return response  # type: ignore


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
)

# app.add_middleware(JwtAccessMiddleware)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.add_middleware(LoggingMiddleware)
app.add_middleware(ExceptionMiddleware)
app.add_middleware(LoggingMiddlewareReq)
app.add_middleware(MetricMiddleware)
app.add_middleware(RawContextMiddleware)
app.add_middleware(CorrelationIdMiddleware)
app.include_router(api_router, prefix=settings.API_PREFIX)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
