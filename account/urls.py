from django.urls import path

from . import views

urlpatterns = [
    path("profile/", views.UserProfileView.as_view(), name="user-profile"),
    path("profile/picture/", views.ProfilePictureView.as_view(), name="profile-picture"),
]