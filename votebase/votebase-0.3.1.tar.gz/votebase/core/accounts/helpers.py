from django.apps import apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist

from votebase.core.utils.common import generate_slug_for_user


def create_user_profile(user, **attrs):
    # get swappable profile model
    profile_model = get_profile_model()

    # create empty profile
    slug = generate_slug_for_user()
    profile = profile_model.objects.create(user=user, slug=slug, **attrs)

    # generate token
    # profile.token = generate_token()
    # profile.save(update_fields=['token'])

    # return new profile
    return profile


def get_user_profile(user):
    # get swappable profile model
    profile_model = get_profile_model()

    # try to profile
    try:
        return profile_model.objects.get(user=user)
    except ObjectDoesNotExist:
        return None


def get_profile_model():
    """
    Returns the Profile model that is active in this project.
    """
    try:
        return apps.get_model(settings.AUTH_PROFILE_MODULE)
    except ValueError:
        raise ImproperlyConfigured("AUTH_PROFILE_MODULE must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "AUTH_PROFILE_MODULE refers to model '%s' that has not been installed" % settings.AUTH_USER_MODEL
        )
