# Standard Library
import datetime
import uuid

# Third-Party
from django_fsm import FSMIntegerField
from django_fsm import transition
from django_fsm_log.decorators import fsm_log_by
from django_fsm_log.decorators import fsm_log_description
from django_fsm_log.models import StateLog
from dry_rest_permissions.generics import allow_staff_or_superuser
from dry_rest_permissions.generics import authenticated_users
from model_utils import Choices
from model_utils.models import TimeStampedModel
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook
from phonenumber_field.modelfields import PhoneNumberField

# Django
from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models
from django.utils.functional import cached_property

# Local
from .fields import ImageUploadPath

class Person(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    STATUS = Choices(
        (-10, 'inactive', 'Inactive',),
        (0, 'new', 'New',),
        (10, 'active', 'Active',),
    )

    status = FSMIntegerField(
        help_text="""DO NOT CHANGE MANUALLY unless correcting a mistake.  Use the buttons to change state.""",
        choices=STATUS,
        default=STATUS.active,
    )

    prefix = models.CharField(
        help_text="""
            The prefix of the person.""",
        max_length=255,
        blank=True,
        default='',
    )

    first_name = models.CharField(
        help_text="""
            The first name of the person.""",
        max_length=255,
    )

    middle_name = models.CharField(
        help_text="""
            The middle name of the person.""",
        max_length=255,
        blank=True,
        default='',
    )

    last_name = models.CharField(
        help_text="""
            The last name of the person.""",
        max_length=255,
    )

    nick_name = models.CharField(
        help_text="""
            The nickname of the person.""",
        max_length=255,
        blank=True,
        default='',
    )

    suffix = models.CharField(
        help_text="""
            The suffix of the person.""",
        max_length=255,
        blank=True,
        default='',
    )

    birth_date = models.DateField(
        blank=True,
        null=True,
    )

    spouse = models.CharField(
        max_length=255,
        blank=True,
        default='',
    )

    location = models.CharField(
        help_text="""
            The geographical location of the resource.""",
        max_length=255,
        blank=True,
        default='',
    )

    PART = Choices(
        (1, 'tenor', 'Tenor'),
        (2, 'lead', 'Lead'),
        (3, 'baritone', 'Baritone'),
        (4, 'bass', 'Bass'),
    )

    part = models.IntegerField(
        choices=PART,
        blank=True,
        null=True,
    )

    mon = models.IntegerField(
        help_text="""
            Men of Note.""",
        blank=True,
        null=True,
    )

    GENDER = Choices(
        (10, 'male', 'Male'),
        (20, 'female', 'Female'),
    )

    gender = models.IntegerField(
        choices=GENDER,
        blank=True,
        null=True,
    )

    representing = models.CharField(
        help_text="""
            Representing (used primarily for judges.)""",
        max_length=10,
        blank=True,
        default='',
    )

    website = models.URLField(
        help_text="""
            The website URL of the resource.""",
        blank=True,
        default='',
    )

    email = models.EmailField(
        help_text="""
            The contact email of the resource.""",
        blank=True,
        null=True,
    )

    address = models.TextField(
        help_text="""
            The complete address of the resource.""",
        max_length=1000,
        blank=True,
        default='',
    )

    home_phone = PhoneNumberField(
        help_text="""
            The home phone number of the resource.  Include country code.""",
        blank=True,
        default='',
    )

    work_phone = PhoneNumberField(
        help_text="""
            The work phone number of the resource.  Include country code.""",
        blank=True,
        default='',
    )

    cell_phone = PhoneNumberField(
        help_text="""
            The cell phone number of the resource.  Include country code.""",
        blank=True,
        default='',
    )

    airports = ArrayField(
        base_field=models.CharField(
            blank=True,
            max_length=3,
        ),
        blank=True,
        null=True,
    )

    image = models.ImageField(
        upload_to=ImageUploadPath('image'),
        blank=True,
        default='',
    )

    description = models.TextField(
        help_text="""
            A bio of the person.  Max 1000 characters.""",
        max_length=1000,
        blank=True,
        default='',
    )

    notes = models.TextField(
        help_text="""
            Notes (for internal use only).""",
        blank=True,
        default='',
    )

    bhs_id = models.IntegerField(
        blank=True,
        null=True,
    )

    # Relations
    owners = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='persons',
        blank=True,
    )

    statelogs = GenericRelation(
        StateLog,
        related_query_name='persons',
    )

    # Properties
    def is_active(self):
        # For Algolia indexing
        return True
        # return bool(
        #     self.officers.filter(
        #         status__gt=0,
        #     )
        # )

    @cached_property
    def usernames(self):
        return [x.username for x in self.owners.all()]

    @cached_property
    def nomen(self):
        if self.nick_name:
            nick = "({0})".format(self.nick_name)
        else:
            nick = ""
        if self.bhs_id:
            suffix = "[{0}]".format(self.bhs_id)
        else:
            suffix = "[No BHS ID]"
        full = "{0} {1} {2} {3} {4}".format(
            self.first_name,
            self.middle_name,
            self.last_name,
            nick,
            suffix,
        )
        return " ".join(full.split())

    @cached_property
    def name(self):
        return self.common_name

    @cached_property
    def full_name(self):
        if self.nick_name:
            nick = "({0})".format(self.nick_name)
        else:
            nick = ""
        full = "{0} {1} {2} {3}".format(
            self.first_name,
            self.middle_name,
            self.last_name,
            nick,
        )
        return " ".join(full.split())

    @cached_property
    def common_name(self):
        if self.nick_name:
            first = self.nick_name
        else:
            first = self.first_name
        return "{0} {1}".format(first, self.last_name)

    @cached_property
    def sort_name(self):
        return "{0}, {1}".format(self.last_name, self.first_name)

    @cached_property
    def initials(self):
        one = self.nick_name or self.first_name
        two = str(self.last_name)
        if not (one and two):
            return "--"
        return "{0}{1}".format(
            one[0].upper(),
            two[0].upper(),
        )

    @cached_property
    def image_id(self):
        return self.image.name or 'missing_image'

    def image_url(self):
        try:
            return self.image.url
        except ValueError:
            return 'https://res.cloudinary.com/barberscore/image/upload/v1554830585/missing_image.jpg'

    # @cached_property
    # def current_through(self):
    #     try:
    #         current_through = self.members.get(
    #             group__bhs_id=1,
    #         ).end_date
    #     except self.members.model.DoesNotExist:
    #         current_through = None
    #     return current_through

    # @cached_property
    # def current_status(self):
    #     today = now().date()
    #     if self.current_through:
    #         if self.current_through >= today:
    #             return True
    #         return False
    #     return True

    # @cached_property
    # def current_district(self):
    #     return bool(
    #         self.members.filter(
    #             group__kind=11, # hardcoded for convenience
    #             status__gt=0,
    #         )
    #     )

    # Internals
    # objects = PersonManager()

    class Meta:
        verbose_name_plural = 'Persons'

    class JSONAPIMeta:
        resource_name = "person"

    def clean(self):
        pass

    def __str__(self):
        return self.nomen

    # Permissions
    @staticmethod
    @allow_staff_or_superuser
    @authenticated_users
    def has_read_permission(request):
        return True

    @allow_staff_or_superuser
    @authenticated_users
    def has_object_read_permission(self, request):
        return True

    @staticmethod
    @allow_staff_or_superuser
    @authenticated_users
    def has_write_permission(request):
        return False

    @allow_staff_or_superuser
    @authenticated_users
    def has_object_write_permission(self, request):
        return False

    # Transitions
    @fsm_log_by
    @fsm_log_description
    @transition(field=status, source='*', target=STATUS.active)
    def activate(self, description=None, *args, **kwargs):
        """Activate the Person."""
        return

    @fsm_log_by
    @fsm_log_description
    @transition(field=status, source='*', target=STATUS.inactive)
    def deactivate(self, description=None, *args, **kwargs):
        """Deactivate the Person."""
        return


class Group(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    name = models.CharField(
        help_text="""
            The name of the resource.
        """,
        max_length=255,
    )

    STATUS = Choices(
        (-10, 'inactive', 'Inactive',),
        (-5, 'aic', 'AIC',),
        (0, 'new', 'New',),
        (10, 'active', 'Active',),
    )

    status = FSMIntegerField(
        help_text="""DO NOT CHANGE MANUALLY unless correcting a mistake.  Use the buttons to change state.""",
        choices=STATUS,
        default=STATUS.new,
    )

    KIND = Choices(
        (32, 'chorus', "Chorus"),
        (41, 'quartet', "Quartet"),
        (46, 'vlq', "VLQ"),
    )

    kind = models.IntegerField(
        help_text="""
            The kind of group.
        """,
        choices=KIND,
    )

    GENDER = Choices(
        (10, 'male', "Male"),
        (20, 'female', "Female"),
        (30, 'mixed', "Mixed"),
    )

    gender = models.IntegerField(
        help_text="""
            The gender of group.
        """,
        choices=GENDER,
    )

    representing = models.CharField(
        max_length=50,
        blank=True,
        default='',
    )

    bhs_id = models.IntegerField(
        help_text="""
            Should *not* be an official BHS ID.""",
        blank=True,
        null=True,
        unique=True,
    )

    code = models.CharField(
        help_text="""
            Short-form code.""",
        max_length=255,
        blank=True,
        default='',
    )

    website = models.URLField(
        help_text="""
            The website URL of the resource.""",
        blank=True,
        default='',
    )

    email = models.EmailField(
        help_text="""
            The contact email of the resource.""",
        blank=True,
        default='',
    )

    phone = PhoneNumberField(
        help_text="""
            The home phone number of the resource.  Include country code.""",
        blank=True,
        default='',
    )

    fax_phone = PhoneNumberField(
        help_text="""
            The home phone number of the resource.  Include country code.""",
        blank=True,
        default='',
    )

    start_date = models.DateField(
        blank=True,
        null=True,
    )

    end_date = models.DateField(
        blank=True,
        null=True,
    )

    location = models.CharField(
        help_text="""
            The geographical location of the resource.""",
        max_length=255,
        blank=True,
        default='',
    )

    facebook = models.URLField(
        help_text="""
            The facebook URL of the resource.""",
        blank=True,
        default='',
    )

    twitter = models.URLField(
        help_text="""
            The twitter URL of the resource.""",
        blank=True,
        default='',
    )

    youtube = models.URLField(
        help_text="""
            The youtube URL of the resource.""",
        blank=True,
        default='',
    )

    pinterest = models.URLField(
        help_text="""
            The pinterest URL of the resource.""",
        blank=True,
        default='',
    )

    flickr = models.URLField(
        help_text="""
            The flickr URL of the resource.""",
        blank=True,
        default='',
    )

    instagram = models.URLField(
        help_text="""
            The instagram URL of the resource.""",
        blank=True,
        default='',
    )

    soundcloud = models.URLField(
        help_text="""
            The soundcloud URL of the resource.""",
        blank=True,
        default='',
    )

    image = models.ImageField(
        upload_to=ImageUploadPath('image'),
        blank=True,
        default='',
    )

    description = models.TextField(
        help_text="""
            A description of the group.  Max 1000 characters.""",
        max_length=1000,
        blank=True,
        default='',
    )

    visitor_information = models.TextField(
        max_length=255,
        blank=True,
        default='',
    )

    participants = models.CharField(
        help_text='Director(s) or Members (listed TLBB)',
        max_length=255,
        blank=True,
        default='',
    )

    chapters = models.CharField(
        help_text="""
            The denormalized chapter representation.""",
        max_length=255,
        blank=True,
        default='',
    )

    notes = models.TextField(
        help_text="""
            Notes (for internal use only).""",
        blank=True,
        default='',
    )

    # FKs
    owners = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='groups',
    )

    # Relations
    statelogs = GenericRelation(
        StateLog,
        related_query_name='groups',
    )

    # Properties
    @cached_property
    def usernames(self):
        return [x.username for x in self.owners.all()]

    @cached_property
    def nomen(self):
        if self.bhs_id:
            suffix = "[{0}]".format(self.bhs_id)
        else:
            suffix = "[No BHS ID]"
        if self.code:
            code = "({0})".format(self.code)
        else:
            code = ""
        full = [
            self.name,
            code,
            suffix,
        ]
        return " ".join(full)

    @cached_property
    def image_id(self):
        return self.image.name or 'missing_image'

    # Group Methods
    # def update_owners(self):
    #     officers = self.officers.filter(
    #         status__gt=0,
    #     )
    #     for officer in officers:
    #         self.owners.add(
    #             officer.person.user,
    #         )
    #     return

    # Algolia
    def is_active(self):
        return bool(self.status == self.STATUS.active)

    def image_url(self):
        try:
            return self.image.url
        except ValueError:
            return 'https://res.cloudinary.com/barberscore/image/upload/v1554830585/missing_image.jpg'

    def owner_ids(self):
        return [str(owner.id) for owner in self.owners.all()]

    # Internals
    # objects = GroupManager()

    class Meta:
        verbose_name_plural = 'Groups'

    class JSONAPIMeta:
        resource_name = "group"

    def __str__(self):
        return self.nomen

    def clean(self):
        return

    # Group Permissions
    @staticmethod
    @allow_staff_or_superuser
    @authenticated_users
    def has_read_permission(request):
        return True

    @allow_staff_or_superuser
    @authenticated_users
    def has_object_read_permission(self, request):
        return True

    @staticmethod
    @allow_staff_or_superuser
    @authenticated_users
    def has_write_permission(request):
        roles = [
            'SCJC',
            'Librarian',
            'Manager',
        ]
        return any(item in roles for item in request.user.roles.values_list('name'))

    @allow_staff_or_superuser
    @authenticated_users
    def has_object_write_permission(self, request):
        return any([
            all([
                'SCJC' in request.user.roles.values_list('name'),
            ]),
            all([
                'Librarian' in request.user.roles.values_list('name'),
            ]),
            all([
                self.owners.filter(id__contains=request.user.id),
            ]),
        ])

    # Conditions:
    def can_activate(self):
        return

    # Transitions
    @fsm_log_by
    @fsm_log_description
    @transition(
        field=status,
        source=[
            STATUS.active,
            STATUS.inactive,
            STATUS.new,
        ],
        target=STATUS.active,
        conditions=[
            can_activate,
        ]
    )
    def activate(self, description=None, *args, **kwargs):
        """Activate the Group."""
        self.denormalize()
        return

    @fsm_log_by
    @fsm_log_description
    @transition(
        field=status,
        source=[
            STATUS.active,
            STATUS.inactive,
            STATUS.new,
        ],
        target=STATUS.inactive,
    )
    def deactivate(self, description=None, *args, **kwargs):
        """Deactivate the Group."""
        return
