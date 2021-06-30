from django.http import HttpRequest, HttpResponse
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from frontend_settings.utils import get_flags, get_settings


@api_view(["GET"])
@permission_classes((permissions.AllowAny,))
def settings(request: HttpRequest) -> HttpResponse:
    data = {"flags": get_flags(request), "settings": get_settings()}
    return Response(data=data, status=status.HTTP_200_OK)
