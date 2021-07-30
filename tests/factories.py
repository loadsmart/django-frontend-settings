import factory
import waffle
from django.contrib.auth import get_user_model

FlagModel = waffle.get_waffle_flag_model()
UserModel = get_user_model()


class FlagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FlagModel


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserModel
