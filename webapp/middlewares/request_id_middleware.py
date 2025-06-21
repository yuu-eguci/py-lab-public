import uuid


class RequestIDMiddleware:
    """
    Middleware that adds a unique request id to the request object.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.request_id = str(uuid.uuid4())[0:8]
        response = self.get_response(request)
        return response
