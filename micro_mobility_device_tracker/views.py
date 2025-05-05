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
from django.contrib.auth.decorators import login_required
import face_recognition
import cv2
import numpy as np
import os


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

def recognize_face(request):
    if not request.user.is_authenticated:
        return redirect("login")

    profile = Profile.objects.get(user=request.user)

    if not profile.owner_image:
        return render(request, "recognize.html", {
            "error": "Please upload your reference photo first."
        })

    if request.method == "POST" and request.FILES.get("test_image"):
        # Save the uploaded test image temporarily
        test_file = request.FILES["test_image"]
        test_path = default_storage.save(f"uploads/{test_file.name}", test_file)

        try:
            # Load and encode owner's face
            owner_image = face_recognition.load_image_file(profile.owner_image.path)
            owner_encoding = face_recognition.face_encodings(owner_image)[0]

            # Load and encode test image
            test_image = face_recognition.load_image_file(default_storage.path(test_path))
            test_locations = face_recognition.face_locations(test_image)
            test_encodings = face_recognition.face_encodings(test_image, test_locations)

            # Compare faces
            results = []
            for encoding in test_encodings:
                match = face_recognition.compare_faces([owner_encoding], encoding, tolerance=0.45)
                results.append("Owner Detected ✅" if match[0] else "Unknown ❌")

            return render(request, "recognize.html", {
                "results": results,
                "owner_image": profile.owner_image.url
            })

        except IndexError:
            return render(request, "recognize.html", {
                "error": "No face found in one of the images.",
                "owner_image": profile.owner_image.url
            })

    return render(request, "recognize.html", {
        "owner_image": profile.owner_image.url if profile.owner_image else None
    })
