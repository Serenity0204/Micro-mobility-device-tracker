from django.urls import path, include
from . import views



urlpatterns = [
    path("", views.home_view, name="home"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("recognize/", views.recognize_face, name="recognize_face"),
    path("upload-owner-image/", views.upload_owner_image, name="upload_owner_image"),
]