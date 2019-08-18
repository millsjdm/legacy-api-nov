# Third-Party
from django_fsm_log.admin import StateLogInline
from fsm_admin.mixins import FSMTransitionMixin
from reversion.admin import VersionAdmin

# Django
from django.contrib import admin

# Local
from .models import Group
from .models import Person

@admin.register(Group)
class GroupAdmin(VersionAdmin, FSMTransitionMixin):
    save_on_top = True
    fsm_field = [
        'status',
    ]
    fields = [
        'id',
        'name',
        'status',
        'kind',
        'gender',
        'representing',
        'owners',
        ('bhs_id', 'code',),
        'location',
        'email',
        'phone',
        'website',
        'image',
        'description',
        'participants',
        'chapters',
        'notes',
        ('created', 'modified',),
    ]

    list_filter = [
        'status',
        'kind',
        'gender',
    ]

    search_fields = [
        'name',
        'bhs_id',
        'code',
    ]

    list_display = [
        'name',
        'kind',
        'gender',
        'representing',
        'bhs_id',
        'code',
        'status',
    ]
    readonly_fields = [
        'id',
        'created',
        'modified',
    ]

    autocomplete_fields = [
        'owners',
        # 'parent',
    ]


@admin.register(Person)
class PersonAdmin(VersionAdmin, FSMTransitionMixin):
    fields = [
        'id',
        'status',
        ('first_name', 'middle_name', 'last_name', 'nick_name',),
        ('email', 'bhs_id', 'birth_date',),
        ('home_phone', 'work_phone', 'cell_phone',),
        ('part', 'gender',),
        'spouse',
        'location',
        'representing',
        'website',
        'image',
        'description',
        'notes',
        'owners',
        ('created', 'modified',),
        # 'user',
    ]

    list_display = [
        'common_name',
        'email',
        'cell_phone',
        'part',
        'gender',
        'status',
    ]

    list_filter = [
        'status',
        'gender',
        'part',
    ]

    raw_id_fields = [
        # 'user',
    ]

    readonly_fields = [
        'id',
        'first_name',
        'middle_name',
        'last_name',
        'nick_name',
        'email',
        'bhs_id',
        'birth_date',
        'part',
        'mon',
        'gender',
        'home_phone',
        'work_phone',
        'cell_phone',
        'common_name',
        'created',
        'modified',
    ]

    fsm_field = [
        'status',
    ]

    search_fields = [
        'last_name',
        'first_name',
        'nick_name',
        'bhs_id',
        'email',
    ]

    autocomplete_fields = [
        'owners',
    ]

    save_on_top = True

    ordering = [
        'last_name',
        'first_name',
    ]
    # readonly_fields = [
    #     'common_name',
    # ]
