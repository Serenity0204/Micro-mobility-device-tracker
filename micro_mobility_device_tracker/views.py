from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from .models import Profile
from django.db import IntegrityError
from django.contrib import messages
from django.http import JsonResponse
from .models import Profile
from .utils import recognize_faces_util
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

ESP32_IP = "http://172.20.10.10"


def esp32_control_page(request):
    return render(request, 'control.html')

def esp32_send_high(request):
    try:
        requests.get(f"{ESP32_IP}/high", timeout=3)
        return redirect('esp32_control')
    except requests.exceptions.RequestException as e:
        return HttpResponse(f"Error sending HIGH: {e}")

def esp32_send_low(request):
    try:
        requests.get(f"{ESP32_IP}/low", timeout=3)
        return redirect('esp32_control')
    except requests.exceptions.RequestException as e:
        return HttpResponse(f"Error sending LOW: {e}")


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


def recognize_faces_util(owner_path, test_path):
    owner_img = face_recognition.load_image_file(owner_path)
    test_img = face_recognition.load_image_file(test_path)

    owner_encodings = face_recognition.face_encodings(owner_img)
    test_encodings = face_recognition.face_encodings(test_img)

    if not owner_encodings:
        return ["❗ No face found in owner's image."]
    if not test_encodings:
        return ["❗ No face found in uploaded image."]

    match = face_recognition.compare_faces([owner_encodings[0]], test_encodings[0])[0]
    return ["✅ Match (Same person)" if match else "❌ No match (Different person)"]

@csrf_exempt
@require_POST
def esp32_upload(request):
    if 'image' not in request.FILES:
        return JsonResponse({"error": "No image provided"}, status=400)

    image = request.FILES["image"]
    image_bytes = image.read()

    try:
        # Convert to image array
        img = Image.open(io.BytesIO(image_bytes))
        img_np = np.array(img)
        face_locations = face_recognition.face_locations(img_np)

        if face_locations:
            # 🔍 Match against logged-in user's profile (for testing, you may default to one user)
            user = request.user if request.user.is_authenticated else User.objects.first()
            profile = user.profile
            owner_path = profile.owner_image.path

            # Save test image
            test_path = os.path.join(settings.MEDIA_ROOT, "temp_test.jpg")
            with open(test_path, "wb") as f:
                f.write(image_bytes)

            # Compare
            results = recognize_faces_util(owner_path, test_path)
            result_text = results[0]

            # Save to faces/
            filename = f"{uuid.uuid4().hex}.jpg"
            filepath = os.path.join(settings.MEDIA_ROOT, "faces", filename)
            with open(filepath, "wb") as f:
                f.write(image_bytes)
            with open(filepath + ".txt", "w") as f:
                f.write(result_text)

            os.remove(test_path)

        else:
            # No face → overwrite latest.jpg
            latest_path = os.path.join(settings.MEDIA_ROOT, "uploads", "latest.jpg")
            os.makedirs(os.path.dirname(latest_path), exist_ok=True)
            with open(latest_path, "wb") as f:
                f.write(image_bytes)

        return JsonResponse({"status": "ok"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def scooter_watch_view(request):
    faces_dir = os.path.join(settings.MEDIA_ROOT, "faces")
    face_images = []
    if os.path.exists(faces_dir):
        for fname in sorted(os.listdir(faces_dir), reverse=True):
            if fname.endswith(".jpg"):
                result_path = os.path.join(faces_dir, fname + ".txt")
                result = "Unknown"
                if os.path.exists(result_path):
                    with open(result_path, "r") as f:
                        result = f.read().strip()
                face_images.append({
                    "url": settings.MEDIA_URL + "faces/" + fname,
                    "result": result,
                    "name": fname,
                })

    latest_img_url = settings.MEDIA_URL + "uploads/latest.jpg"

    return render(request, "scooter_watch.html", {
        "face_images": face_images,
        "latest_img": latest_img_url,
        "timestamp": now().timestamp(),  # ← add this
    })

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
    return redirect("scooter_watch")