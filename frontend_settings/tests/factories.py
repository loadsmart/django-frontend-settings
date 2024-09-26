import factory


class FeatureToggleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "featureflag.FeatureToggle"
        django_get_or_create = ("name",)

    enabled = True
    everyone = False


class FeatureToggleMappingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "featureflag.FeatureToggleMapping"

    feature_toggle = factory.SubFactory(
        "rfp_backend.featureflag._tests.factories.FeatureToggleFactory",
    )
