from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path("admin-dashboard", views.dashboard_admin, name="dashboard-admin"),
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("", views.home, name="home"),
    path("add-building", views.add_building, name="add-building"),
    path("delete-building/<int:number>", views.delete_building, name="delete_building"),
    path("edit-building/<int:number>", views.edit_building, name="edit-building"),
    path("add-entrance", views.add_entrance, name="add-entrance"),
    path(
        "edit-entrance/<int:building_number>", views.edit_entrance, name="edit-entrance"
    ),
    path("delete-entrance/<int:number>", views.delete_entrance, name="delete_entrance"),
    path("add-apartment", views.add_apartment, name="add-apartment"),
    path(
        "edit-apartment/<int:building_number>/",
        views.edit_apartment,
        name="edit-apartment",
    ),
    path(
        "delete-apartment/<int:number>", views.delete_apartment, name="delete-apartment"
    ),
    path("event-log/", views.view_event_log, name="event-log"),
]
