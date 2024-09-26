from rest_framework import serializers


class FeatureMappingRequestSerializer(serializers.Serializer):
    feature_names = serializers.ListField(child=serializers.CharField(), required=True)
    entity_name = serializers.CharField(required=False)
    entity_uuid = serializers.UUIDField(required=False)
