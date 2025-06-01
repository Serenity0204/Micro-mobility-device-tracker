from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # Account
    path("", views.home_view, name="home"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),

    # Computer Vision
    path("upload-owner-image/", views.upload_owner_image, name="upload_owner_image"),
    path("delete-face-image/", views.delete_face_image, name="delete_face_image"),
    path("unlock-with-face/", views.unlock_with_face, name="unlock_with_face"),

    # ESP32
    path("esp32/toggle-lock/", views.esp32_toggle_lock, name="esp32_toggle_lock"),
    path('esp32/send-gps-location/', views.esp32_send_gps_location, name="esp32_send_gps_location"),
    # ESP32 CAM
    path("owner-unlock/", views.owner_unlock_view, name="owner_unlock"),
    path("capture-snapshot/", views.capture_snapshot, name="capture_snapshot"),
    path("view-suspect/", views.view_suspect, name="view_suspect"),
    path("update-suspect/", views.update_suspect_snapshot, name="update_suspect"),    
    # Location
    path("view-gps-location/", views.view_gps_location, name="view_gps_location"),
    path("get-latest-gps-location/", views.get_latest_gps_location, name="get_latest_gps_location"),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)