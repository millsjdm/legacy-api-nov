
# Standard Library
import logging

# Third-Party
from django_fsm import TransitionNotAllowed
from dry_rest_permissions.generics import DRYPermissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.negotiation import BaseContentNegotiation
from rest_framework.response import Response
from rest_framework_json_api.django_filters import DjangoFilterBackend

# Django
from django.utils.text import slugify

# Local
from .filtersets import GroupFilterset
from .filtersets import PersonFilterset
from .models import Group
from .models import Person
from .serializers import GroupSerializer
from .serializers import PersonSerializer

log = logging.getLogger(__name__)


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.select_related(
        # 'owner',
        # 'parent',
    ).prefetch_related(
        # 'owners',
        # 'children',
        # 'awards',
        # 'appearances',
        # 'conventions',
        # 'entries',
        # 'members',
        # 'members__person',
        # 'officers',
        # 'officers__person',
        # 'repertories',
        # 'repertories__chart',
        # 'statelogs',
    )
    serializer_class = GroupSerializer
    filterset_class = GroupFilterset
    filter_backends = [
        DjangoFilterBackend,
    ]
    permission_classes = [
        DRYPermissions,
    ]
    resource_name = "group"

    @action(methods=['post'], detail=True)
    def activate(self, request, pk=None, **kwargs):
        object = self.get_object()
        try:
            object.activate(by=self.request.user)
        except TransitionNotAllowed:
            return Response(
                {'status': 'Transition conditions not met.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        object.save()
        serializer = self.get_serializer(object)
        return Response(serializer.data)

    @action(methods=['post'], detail=True)
    def deactivate(self, request, pk=None, **kwargs):
        object = self.get_object()
        try:
            object.deactivate(by=self.request.user)
        except TransitionNotAllowed:
            return Response(
                {'status': 'Transition conditions not met.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        object.save()
        serializer = self.get_serializer(object)
        return Response(serializer.data)


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.select_related(
        # 'user',
    ).prefetch_related(
        # 'assignments',
        # 'members',
        # 'officers',
        # 'panelists',
        # 'statelogs',
    )
    serializer_class = PersonSerializer
    filterset_class = PersonFilterset
    filter_backends = [
        DjangoFilterBackend,
    ]
    permission_classes = [
        DRYPermissions,
    ]
    resource_name = "person"

    @action(methods=['post'], detail=True)
    def activate(self, request, pk=None, **kwargs):
        object = self.get_object()
        try:
            object.activate(by=self.request.user)
        except TransitionNotAllowed:
            return Response(
                {'status': 'Transition conditions not met.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        object.save()
        serializer = self.get_serializer(object)
        return Response(serializer.data)

    @action(methods=['post'], detail=True)
    def deactivate(self, request, pk=None, **kwargs):
        object = self.get_object()
        try:
            object.deactivate(by=self.request.user)
        except TransitionNotAllowed:
            return Response(
                {'status': 'Transition conditions not met.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        object.save()
        serializer = self.get_serializer(object)
        return Response(serializer.data)
