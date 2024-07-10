from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .models import Building, Entrance


def admin_required(
    function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None
):
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_admin(),
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def manager_required(
    function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None
):
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_manager(),
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def guard_required(
    function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None
):
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_guard(),
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def manager_of_building_required(view_func):
    def wrapper(request, building_id, *args, **kwargs):
        building = get_object_or_404(Building, id=building_id)
        if request.user.is_admin() or (
            request.user.is_manager() and building.manager == request.user
        ):
            return view_func(request, building_id, *args, **kwargs)
        raise PermissionDenied

    return wrapper


def guard_of_entrance_required(view_func):
    def wrapper(request, entrance_id, *args, **kwargs):
        entrance = get_object_or_404(Entrance, id=entrance_id)
        if (
            request.user.is_admin()
            or request.user.is_manager()
            or entrance.guard == request.user
        ):
            return view_func(request, entrance_id, *args, **kwargs)
        raise PermissionDenied

    return wrapper
