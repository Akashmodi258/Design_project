import face_recognition
import cv2
import numpy as np
from io import BytesIO
from PIL import Image
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import UserRegistrationForm, LoginForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ResumeForm, UserUpdateForm
from .models import Resume, User
from django.http import FileResponse, Http404
from django.contrib.auth import get_user_model

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            profile_photo = request.FILES['profile_photo']

            # Convert the uploaded image to 8-bit gray using OpenCV
            try:
                # Read the image using OpenCV
                img = cv2.imdecode(np.fromstring(profile_photo.read(), np.uint8), cv2.IMREAD_COLOR)

                # Convert to grayscale
                gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                # Convert back to RGB format for face recognition
                rgb_img = cv2.cvtColor(gray_img, cv2.COLOR_GRAY2RGB)

                # Save the image into a BytesIO object for face recognition
                img_io = BytesIO()
                _, buffer = cv2.imencode('.jpg', rgb_img)
                img_io.write(buffer)
                img_io.seek(0)

                # Load the image for face recognition
                new_user_image = face_recognition.load_image_file(img_io)

            except Exception as e:
                messages.error(request, f"Error processing the image: {str(e)}")
                return render(request, 'users/register.html', {'form': form})

            # Detect face encodings
            try:
                new_user_encoding = face_recognition.face_encodings(new_user_image)[0]
            except IndexError:
                messages.error(request, "Unable to detect a face in the photo. Please upload a clear photo.")
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
    try:
        resume = Resume.objects.get(user=user)
    except Resume.DoesNotExist:
        resume = None

    if request.method == 'POST':
        if 'delete_account' in request.POST:
            user.delete()
            messages.success(request, 'Your account has been deleted.')
            return redirect('home')  # Redirect to home or another page
        elif 'update_profile' in request.POST:
            form = UserUpdateForm(request.POST, request.FILES, instance=user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your profile has been updated!')
                return redirect('dashboard')  # Redirect to dashboard or another page

    form = UserUpdateForm(instance=user)
    
    context = {
        'resume': resume,
        'form': form,
    }
    return render(request, 'dashboard.html', context)

def home(request):
    return render(request, 'users/home.html')



@login_required
def upload_resume(request):
    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES)
        if form.is_valid():
            resume, created = Resume.objects.get_or_create(user=request.user)
            resume.file = form.cleaned_data['file']
            resume.save()
            return redirect('dashboard')  # Redirect to dashboard or another appropriate page
    else:
        form = ResumeForm()
    return render(request, 'users/upload_resume.html', {'form': form})

@login_required
def update_resume(request):
    resume = get_object_or_404(Resume, user=request.user)
    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES, instance=resume)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ResumeForm(instance=resume)
    return render(request, 'users/update_resume.html', {'form': form})

@login_required
def delete_resume(request):
    resume = get_object_or_404(Resume, user=request.user)
    if request.method == 'POST':
        resume.delete()
        return redirect('dashboard')
    return render(request, 'users/confirm_delete_resume.html', {'resume': resume})


@login_required
def download_resume(request):
    resume = get_object_or_404(Resume, user=request.user)
    file_path = resume.file.path
    try:
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=resume.file.name)
    except FileNotFoundError:
        raise Http404("Resume file not found")
    
    
    

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