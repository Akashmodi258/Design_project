import face_recognition
import numpy as np
from io import BytesIO
from PIL import Image as PILImage
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import UserRegistrationForm, LoginForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import  UserUpdateForm
from .models import  User
from django.http import FileResponse, Http404
from django.contrib.auth import get_user_model

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            profile_photo = request.FILES['profile_photo']

            # Check for valid image formats
            if profile_photo.content_type not in ['image/jpeg', 'image/png', 'image/bmp']:
                messages.error(request, "Unsupported image format. Please upload a JPEG, PNG, or BMP image.")
                return render(request, 'users/register.html', {'form': form})

            # Convert the uploaded image to grayscale using PIL
            try:
                img_data = BytesIO(profile_photo.read())
                new_user_image = PILImage.open(img_data).convert('RGB')  # Convert to RGB for face recognition
                
                # Convert the image to a NumPy array for face_recognition
                image_np = np.array(new_user_image)
                new_user_encoding = face_recognition.face_encodings(image_np)[0]
            except IndexError:
                messages.error(request, "Unable to detect a face in the photo. Please upload a clear photo.")
                return render(request, 'users/register.html', {'form': form})
            except Exception as e:
                messages.error(request, f"Error processing the image: {str(e)}")
                return render(request, 'users/register.html', {'form': form})

            # Check if this face already exists in the database
            for user in User.objects.all():
                if user.profile_photo:
                    existing_user_image = face_recognition.load_image_file(user.profile_photo.path)
                    existing_user_encoding = face_recognition.face_encodings(existing_user_image)

                    if existing_user_encoding:
                        result = face_recognition.compare_faces([existing_user_encoding[0]], new_user_encoding)
                        if result[0]:
                            messages.error(request, "This face is already registered with another account.")
                            return render(request, 'users/register.html', {'form': form})

            # If no matching face, save the new user
            user = form.save()
            login(request, user)  # Log the user in after successful registration
            return redirect('dashboard')  # Redirect to the dashboard or home page
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()

    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                return redirect('dashboard')  
            else:
                messages.error(request, "Invalid email or password.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = LoginForm()

    return render(request, 'users/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard(request):
    user = request.user

    if request.method == 'POST':
        if 'delete_account' in request.POST:
            user.delete()
            messages.success(request, 'Your account has been deleted.')
            return redirect('home')  
        elif 'update_profile' in request.POST:
            form = UserUpdateForm(request.POST, request.FILES, instance=user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your profile has been updated!')
                return redirect('dashboard')  

    form = UserUpdateForm(instance=user)
    
    context = {
        'form': form,
    }
    return render(request, 'dashboard.html', context)


def home(request):
    return render(request, 'users/home.html')


    
User = get_user_model()

@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('dashboard')
    else:
        form = UserUpdateForm(instance=user)
    
    return render(request, 'users/edit_profile.html', {'form': form})

@login_required
def delete_account(request):
    user = request.user
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Your account has been deleted.')
        return redirect('home')  
    return render(request, 'users/confirm_delete_account.html')
