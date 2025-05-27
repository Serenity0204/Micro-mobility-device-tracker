from django.urls import path, include
from . import views



urlpatterns = [
    path("", views.home_view, name="home"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("recognize/", views.recognize_face_view, name="recognize_face"),
    path("upload-owner-image/", views.upload_owner_image, name="upload_owner_image"),
    # ESP32 test
    path('esp32/', views.esp32_control_page, name='esp32_control'),
    path('esp32/high/', views.esp32_send_high, name='esp32_high'),
    path('esp32/low/', views.esp32_send_low, name='esp32_low'),
]