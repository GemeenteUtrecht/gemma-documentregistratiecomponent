import logging

from django.http import HttpRequest

logger = logging.getLogger(__name__)


class LogHeadersMiddleware:
    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        self.log(request)
        return self.get_response(request) if self.get_response else None

    def log(self, request: HttpRequest):
        user_agent = request.headers.get("User-Agent")
        if user_agent and user_agent.startswith("kube-probe"):
            return
        logger.debug("Request headers for %s: %r", request.path, request.headers)
