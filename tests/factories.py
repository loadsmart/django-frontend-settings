from typing import Generic, TypeVar

import factory
import waffle
from django.contrib.auth import get_user_model

T = TypeVar("T")
FlagModel = waffle.get_waffle_flag_model()
UserModel = get_user_model()


class BaseFactory(Generic[T], factory.django.DjangoModelFactory):
    """This is a workaround to get type hints to play nice with factory boy."""

    @classmethod
    def create(cls, **kwargs) -> T:
        return super().create(**kwargs)


class FlagFactory(BaseFactory[FlagModel]):
    class Meta:
        model = FlagModel


class UserFactory(BaseFactory[UserModel]):
    class Meta:
        model = UserModel
