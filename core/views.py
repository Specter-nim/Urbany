from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"]) 
@permission_classes([AllowAny])
def ok_view(request):
    """Public root view used for validation; always returns 200 OK.
    It does not expose sensitive data and serves as a health/availability marker
    for base paths like /api/contacts/, /api/messages/, etc.
    """
    return Response({"status": "ok"}, status=200)