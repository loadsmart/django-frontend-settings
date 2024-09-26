import uuid

from django.urls import reverse
from rest_framework import status
from frontend_settings.tests.factories import (
    FeatureToggleFactory,
    FeatureToggleMappingFactory,
)


class TestFeatureToggleView:
    def test_should_return_empty_list(self, shipper, shipper_client):
        result = shipper_client.post(
            reverse("featureflag:feature-mappings"),
            json={
                "feature_names": [],
                "entity_name": "shipper",
                "entity_uuid": str(shipper.uuid),
            },
        )
        assert result.status_code == status.HTTP_200_OK
        assert result.json() == {}

    def test_should_work_when_everyone_and_providing_entity_info(
        self, shipper, shipper_client
    ):
        expected_response = {"SOME_TOGGLE": True, "SOME_FLAG": False}
        [
            FeatureToggleFactory(name=feat, enabled=enabled, everyone=True)
            for feat, enabled in expected_response.items()
        ]

        # It should work providing entity info
        payload = {
            "feature_names": list(expected_response.keys()),
            "entity_name": "shipper",
            "entity_uuid": str(shipper.uuid),
        }
        result = shipper_client.post(
            reverse("featureflag:feature-mappings"),
            json=payload,
        )
        assert result.status_code == status.HTTP_200_OK
        assert result.json() == expected_response

    def test_should_work_when_everyone_and_not_providing_entity_info(
        self, shipper, shipper_client
    ):
        expected_response = {"SOME_TOGGLE": True, "SOME_FLAG": False}
        [
            FeatureToggleFactory(name=feat, enabled=enabled, everyone=True)
            for feat, enabled in expected_response.items()
        ]

        # It should work NOT providing entity info
        payload = {
            "feature_names": list(expected_response.keys()),
        }
        result = shipper_client.post(
            reverse("featureflag:feature-mappings"),
            json=payload,
        )
        assert result.status_code == status.HTTP_200_OK
        assert result.json() == expected_response

    def test_should_work_when_not_everyone(self, shipper, shipper_client):
        features = {"SOME_TOGGLE": True, "SOME_FLAG": True}
        any_other_uuid = uuid.uuid4()
        [
            FeatureToggleMappingFactory(
                feature_toggle=FeatureToggleFactory(
                    name=feat, enabled=enabled, everyone=False
                ),
                entity_name="shipper",
                entity_uuid=any_other_uuid,
            )
            for feat, enabled in features.items()
        ]

        # It should work providing entity info
        payload = {
            "feature_names": list(features.keys()),
            "entity_name": "shipper",
            "entity_uuid": str(shipper.uuid),
        }
        result = shipper_client.post(
            reverse("featureflag:feature-mappings"),
            json=payload,
        )
        assert result.status_code == status.HTTP_200_OK

        expectec_result = {"SOME_TOGGLE": False, "SOME_FLAG": False}
        assert result.json() == expectec_result

    def test_should_work_when_not_everyone_with_others(self, shipper, shipper_client):
        features = {"SOME_TOGGLE": True, "SOME_FLAG": True, "ANOTHER_FLAG": True}
        any_other_uuid = uuid.uuid4()
        [
            FeatureToggleMappingFactory(
                feature_toggle=FeatureToggleFactory(
                    name=feat, enabled=enabled, everyone=False
                ),
                entity_name="shipper",
                entity_uuid=any_other_uuid,
            )
            for feat, enabled in features.items()
        ]
        FeatureToggleMappingFactory(
            feature_toggle=FeatureToggleFactory(
                name="ANOTHER_FLAG", enabled=True, everyone=False
            ),
            entity_name="shipper",
            entity_uuid=str(shipper.uuid),
        )

        # It should work providing entity info
        payload = {
            "feature_names": list(features.keys()),
            "entity_name": "shipper",
            "entity_uuid": str(shipper.uuid),
        }
        result = shipper_client.post(
            reverse("featureflag:feature-mappings"),
            json=payload,
        )
        assert result.status_code == status.HTTP_200_OK

        expectec_result = {
            "SOME_TOGGLE": False,
            "SOME_FLAG": False,
            "ANOTHER_FLAG": True,
        }
        assert result.json() == expectec_result
