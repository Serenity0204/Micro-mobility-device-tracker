from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from .models import Profile
from django.db import IntegrityError
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import requests
from django.views.decorators.csrf import csrf_exempt
import os
from django.conf import settings
from django.utils.timezone import now
from django.views.decorators.http import require_POST
from PIL import Image
import numpy as np
import face_recognition
import io
import uuid
import logging
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.views.decorators.http import require_GET



ESP32_IP = "http://172.20.10.11/"
ESP32_CAM_IP = "http://172.20.10.8"

LOCK_FILE = os.path.join(settings.BASE_DIR, "lock_state.txt")

def is_locked():
    return os.path.exists(LOCK_FILE)

def set_lock_state(state):
    if state:
        with open(LOCK_FILE, "w") as f:
            f.write("locked")
    else:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)

def recognize_faces_util(owner_path, test_path):
    owner_img = face_recognition.load_image_file(owner_path)
    test_img = face_recognition.load_image_file(test_path)

    owner_encodings = face_recognition.face_encodings(owner_img)
    test_encodings = face_recognition.face_encodings(test_img)

    if not owner_encodings:
        return ["❗ No face found in owner's image."]
    if not test_encodings:
        return ["❗ No face found in uploaded image."]

    match = face_recognition.compare_faces([owner_encodings[0]], test_encodings[0], tolerance=0.4)[0]
    return ["✅ Match (Same person)" if match else "❌ No match (Different person)"]


def set_esp32_unlock_mode():
    return requests.get(f"{ESP32_IP}/unlock-mode", timeout=5)

def set_esp32_lock_mode():
    return requests.get(f"{ESP32_IP}/lock-mode", timeout=5)


@login_required
def esp32_toggle_lock(request):
    try:
        currently_locked = is_locked()

        if currently_locked:
            response = set_esp32_unlock_mode()
        else:
            response = set_esp32_lock_mode()

        if response.status_code == 200:
            set_lock_state(not currently_locked)
            return redirect("view_suspect")
        return HttpResponse(f"ESP32 returned error: {response.text}", status=500)
    except requests.exceptions.RequestException as e:
        return HttpResponse(f"Failed to contact ESP32: {e}", status=500)



@login_required
def esp32_gps_location(request):
    return render(request, "home.html")




@login_required
def owner_unlock_view(request):
    return render(request, "owner_unlock.html")

@login_required
def capture_snapshot(request):
    try:
        response = requests.get(f"{ESP32_CAM_IP}/capture", timeout=5)
        if response.status_code == 200:
            path = os.path.join("media", "captured.jpg")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as f:
                f.write(response.content)

            profile = request.user.profile
            owner_path = profile.owner_image.path

            result = recognize_faces_util(owner_path, path)[0]

            # Auto-unlock if match
            set_green = False

            if "✅" in result:
                set_lock_state(False)
                set_green = True
            
            return render(request, "owner_unlock.html", {
                "match_result": result,
                "captured_img_url": "/media/captured.jpg",
                "set_green" : set_green,
            })

        return HttpResponse("Failed to capture image", status=500)
    except Exception as e:
        return HttpResponse(f"Error: {e}", status=500)


@login_required
def view_suspect(request):
    # Suspect image (latest activity)
    image_path = os.path.join("media", "suspect.jpg")
    image_url = "/media/suspect.jpg" if os.path.exists(image_path) else None

    # Intrusion images (with faces)
    faces_dir = os.path.join(settings.MEDIA_ROOT, "faces")
    face_images = []
    if os.path.exists(faces_dir):
        for fname in sorted(os.listdir(faces_dir), reverse=True):
            if fname.endswith(".jpg"):
                txt_path = os.path.join(faces_dir, fname + ".txt")
                result = "Unknown"
                if os.path.exists(txt_path):
                    with open(txt_path, "r") as f:
                        result = f.read().strip()
                face_images.append({
                    "url": settings.MEDIA_URL + "faces/" + fname,
                    "result": result,
                    "name": fname,
                })

    return render(request, "view_suspect.html", {
    "image_url": image_url,
    "is_locked": is_locked(),
    "face_images": face_images,  # ← add this
    "timestamp": now().timestamp(),  # optional but useful for forcing refresh
})


@login_required
@require_GET
def update_suspect_snapshot(request):
    if not is_locked():
        return JsonResponse({"status": "inactive"})

    try:
        response = requests.get(f"{ESP32_CAM_IP}/capture", timeout=5)
        if response.status_code != 200:
            return JsonResponse({"status": "failed"}, status=500)

        image_bytes = response.content
        img = Image.open(io.BytesIO(image_bytes))
        img_np = np.array(img)
        face_locations = face_recognition.face_locations(img_np)

        if face_locations:
            # Save with result if face found
            profile = request.user.profile
            owner_path = profile.owner_image.path

            # Save temp
            temp_path = os.path.join(settings.MEDIA_ROOT, "temp_test.jpg")
            with open(temp_path, "wb") as f:
                f.write(image_bytes)

            result = recognize_faces_util(owner_path, temp_path)[0]

            # Save into faces/
            if "✅" not in result:  # Only save if it's NOT the owner
                filename = f"{uuid.uuid4().hex}.jpg"
                face_path = os.path.join(settings.MEDIA_ROOT, "faces", filename)
                os.makedirs(os.path.dirname(face_path), exist_ok=True)
                with open(face_path, "wb") as f:
                    f.write(image_bytes)
                with open(face_path + ".txt", "w") as f:
                    f.write(result)


            os.remove(temp_path)

        else:
            # Overwrite suspect.jpg (no face)
            suspect_path = os.path.join(settings.MEDIA_ROOT, "suspect.jpg")
            with open(suspect_path, "wb") as f:
                f.write(image_bytes)

        return JsonResponse({"status": "success"})

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)




# Create your views here.
@login_required
def upload_owner_image(request):
    profile = request.user.profile

    if request.method == 'POST' and request.FILES.get('owner_image'):
        profile.owner_image = request.FILES['owner_image']
        profile.save()

    return render(request, 'upload_owner.html', {'profile': profile})

def home_view(request):
    request.session.set_expiry(900)
    return render(request, "home.html")

def login_view(request):
    if request.user.is_authenticated:
        request.session.set_expiry(
            900
        )  # Reset session expiry to 15 minutes (900 seconds)
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        # login if authenticate success
        if user is not None:
            login(request, user)
            request.session.set_expiry(
                900
            )  # Set session expiry to 15 minutes (900 seconds)
            return redirect("home")
        else:
            message = "Incorrect Username or Password Entered"
            messages.error(request, message)
            return render(request, "login.html")
    else:
        return render(request, "login.html")
    

def register_view(request):
    if request.user.is_authenticated:
        request.session.set_expiry(
            900
        )  # Reset session expiry to 15 minutes (900 seconds)
        return redirect("home")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")
        # throw error when user exists
        try:
            user = User.objects.create_user(
                username=username, password=password, email=email
            )
            login(request, user)
            request.session.set_expiry(
                900
            )  # Set session expiry to 15 minutes (900 seconds)
            return redirect("home")
        except IntegrityError:
            messages.error(request, "Username Already Exists")
            return redirect("register")
    else:
        return render(request, "register.html")


def logout_view(request):
    logout(request)
    messages.success(request, "User Logged Out")
    return redirect("login")





@require_POST
def delete_face_image(request):
    filename = request.POST.get("filename")
    if filename:
        img_path = os.path.join(settings.MEDIA_ROOT, "faces", filename)
        txt_path = img_path + ".txt"
        try:
            os.remove(img_path)
            if os.path.exists(txt_path):
                os.remove(txt_path)
        except FileNotFoundError:
            pass
    return JsonResponse({"status": "ok"})


@require_GET
def unlock_with_face(request):
    try:
        # Capture from ESP32-CAM
        response = requests.get(f"{ESP32_CAM_IP}/capture", timeout=10)
        if response.status_code != 200:
            return JsonResponse({"message": "Failed to capture image", "unlocked": False})

        image_bytes = response.content
        img = Image.open(io.BytesIO(image_bytes))
        img_np = np.array(img)
        face_locations = face_recognition.face_locations(img_np)

        if not face_locations:
            return JsonResponse({"message": "No face detected", "unlocked": False})

        # Match with owner's image
        user = User.objects.first()
        profile = user.profile
        owner_path = profile.owner_image.path

        test_path = os.path.join(settings.MEDIA_ROOT, "temp_unlock.jpg")
        with open(test_path, "wb") as f:
            f.write(image_bytes)

        result = recognize_faces_util(owner_path, test_path)[0]
        os.remove(test_path)

        if "✅" in result:
            set_lock_state(False)  # Unlock
            return JsonResponse({"message": "✅ Owner verified. Monitoring stopped.", "unlocked": True})
        else:
            return JsonResponse({"message": "❌ Face does not match owner.", "unlocked": False})

    except Exception as e:
        return JsonResponse({"message": f"Error: {str(e)}", "unlocked": False}, status=500)
    

    