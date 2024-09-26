from django.db import models


class TimestampedModel(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FeatureToggle(TimestampedModel):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    enabled = models.BooleanField(default=False)
    everyone = models.BooleanField(default=False, db_index=True)
    notes = models.CharField(max_length=2056, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["name", "everyone"]),
            models.Index(fields=["name", "enabled", "everyone"]),
        ]

    def is_enabled(self, entity_name=None, entity_uuid=None):
        if not self.enabled:
            return False

        if self.everyone:
            return True

        if entity_name and entity_uuid:
            mapping = self.mappings.filter(
                entity_name=entity_name,
                entity_uuid=entity_uuid,
            )

            return mapping.exists()

        return False


class FeatureToggleMapping(TimestampedModel):
    feature_toggle = models.ForeignKey(
        FeatureToggle,
        null=False,
        on_delete=models.CASCADE,
        related_name="mappings",
    )
    entity_name = models.CharField(max_length=100)
    entity_uuid = models.UUIDField(null=False, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["entity_name", "entity_uuid"]),
            models.Index(fields=["feature_toggle", "entity_name", "entity_uuid"]),
        ]
