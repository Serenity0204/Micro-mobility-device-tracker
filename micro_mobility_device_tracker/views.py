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
from django.shortcuts import render, redirect
from django.http import HttpResponse
import requests

ESP32_IP = "http://172.20.10.10"


def esp32_control_page(request):
    return render(request, 'control.html')

def esp32_send_high(request):
    try:
        requests.get(f"{ESP32_IP}/H", timeout=3)
        return redirect('esp32_control')
    except requests.exceptions.RequestException as e:
        return HttpResponse(f"Error sending HIGH: {e}")

def esp32_send_low(request):
    try:
        requests.get(f"{ESP32_IP}/L", timeout=3)
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


def recognize_face_view(request):
    if not request.user.is_authenticated:
        return redirect("login")

    profile = Profile.objects.get(user=request.user)

    if not profile.owner_image:
        context = {"error": "Please upload your reference photo first."}
        return render(request, "recognize.html", context)

    if request.method == "POST" and request.FILES.get("test_image"):
        # Save the uploaded test image temporarily
        test_file = request.FILES["test_image"]
        test_path = default_storage.save(f"uploads/{test_file.name}", test_file)
        owner_image_path = profile.owner_image.path
        try:
            # wait up to 10s or change as needed
            results = recognize_faces_util(owner_image_path, test_path)
            context = {
                "results": results,
                "owner_image": profile.owner_image.url
            }

            return render(request, "recognize.html", context)

        except Exception as e:
            context = {
                "error": str(e),
                "owner_image": profile.owner_image.url
            }
            return render(request, "recognize.html", context)
    context = {
        "owner_image": profile.owner_image.url if profile.owner_image else None
    }
    
    return render(request, "recognize.html", context)
