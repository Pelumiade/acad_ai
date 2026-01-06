import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory

User = get_user_model()


class UserFactory(DjangoModelFactory):

    class Meta:
        model = User
        skip_postgeneration_save = True

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    role = "STUDENT"
    is_active = True

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        if create:
            password = extracted if extracted else "testpass123"
            obj.set_password(password)
            obj.save()
