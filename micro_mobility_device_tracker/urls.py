from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("", views.home_view, name="home"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("upload-owner-image/", views.upload_owner_image, name="upload_owner_image"),
    path("delete-face-image/", views.delete_face_image, name="delete_face_image"),
    path("unlock-with-face/", views.unlock_with_face, name="unlock_with_face"),
    path("toggle-lock/", views.toggle_lock, name="toggle_lock"),
    # ESP32 test
    path('esp32/', views.esp32_control_page, name='esp32_control'),
    path('esp32/high/', views.esp32_send_high, name='esp32_high'),
    path('esp32/low/', views.esp32_send_low, name='esp32_low'),
    path('esp32/gps-location/', views.esp32_gps_location, name="esp32_gps_location"),
    # ESP32 CAM
    path("owner-unlock/", views.owner_unlock_view, name="owner_unlock"),
    path("capture-snapshot/", views.capture_snapshot, name="capture_snapshot"),
    path("view-suspect/", views.view_suspect, name="view_suspect"),
    path("update-suspect/", views.update_suspect_snapshot, name="update_suspect"),    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)