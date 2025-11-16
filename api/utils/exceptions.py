from rest_framework.views import exception_handler
from rest_framework import status

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        custom_data = {
            "success": False,
            "message": str(exc),
            "errors": response.data,
            "status_code": response.status_code,
        }
        response.data = custom_data
    else:
        # Handle uncaught exceptions
        custom_data = {
            "success": False,
            "message": "Internal server error.",
            "errors": str(exc),
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR
        }
        from rest_framework.response import Response
        response = Response(custom_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return response
