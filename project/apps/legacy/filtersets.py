# Third-Party
from django_filters.rest_framework import FilterSet

# Local
from .models import Group
from .models import Person


class GroupFilterset(FilterSet):
    class Meta:
        model = Group
        fields = {
            'owners': [
                'exact',
            ],
            'status': [
                'exact',
                'gt',
            ],
            'kind': [
                'gt',
            ],
            'created': [
                'gt',
            ],
            'modified': [
                'gt',
            ],
        }


class PersonFilterset(FilterSet):
    class Meta:
        model = Person
        fields = {
            # 'user': [
            #     'exact',
            # ],
            # 'user__username': [
            #     'exact',
            # ],
            'status': [
                'exact',
            ],
            'created': [
                'gt',
            ],
            'modified': [
                'gt',
            ],
        }
