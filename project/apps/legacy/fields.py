# Standard Library
import os

# Third-Party
import six

# Django
from django.utils.deconstruct import deconstructible


@deconstructible
class ImageUploadPath(object):

    def __init__(self, name):
        self.name = name

    def __call__(self, instance, filename):
        return os.path.join(
            instance._meta.app_label,
            instance._meta.model_name,
            self.name,
            str(instance.id),
        )
