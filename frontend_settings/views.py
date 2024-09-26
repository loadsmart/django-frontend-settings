from django.http import HttpRequest, HttpResponse
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from frontend_settings.models import FeatureToggle
from frontend_settings.serializers import FeatureMappingRequestSerializer
from frontend_settings.utils import get_flags, get_settings


@api_view(["GET"])
@permission_classes((permissions.AllowAny,))
def settings(request: HttpRequest) -> HttpResponse:
    data = {"flags": get_flags(request), "settings": get_settings()}
    return Response(data=data, status=status.HTTP_200_OK)


class FeatureMappingView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = FeatureMappingRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        feature_names = serializer.validated_data["feature_names"]
        entity_name = serializer.validated_data.get("entity_name")
        entity_uuid = serializer.validated_data.get("entity_uuid")

        feature_toggles = FeatureToggle.objects.filter(name__in=feature_names)
        result = {
            feature.name: feature.is_enabled(
                entity_name=entity_name, entity_uuid=entity_uuid
            )
            for feature in feature_toggles
        }

        return Response(result, status=status.HTTP_200_OK)
