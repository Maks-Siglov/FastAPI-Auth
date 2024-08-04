import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

log = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        request_netloc = request.url.netloc
        request_method = request.method
        route = request.url.path

        response = await call_next(request)
        response_status_code = response.status_code
        process_time = time.time() - start_time
        process_time_formatted = f"{process_time:.4f} seconds"

        log.info(
            f"Request: {request_netloc} {request_method} {route}, "
            f"Response: {response_status_code}, "
            f"Processing time: {process_time_formatted}"
        )

        return response
