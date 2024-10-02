from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Resume
from django.contrib.auth import get_user_model

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['profile_photo', 'first_name', 'middle_name', 'last_name','email', 'password1', 'password2']

class LoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email')
    
    
    
class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['file']


User = get_user_model()

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'middle_name', 'last_name', 'email', 'profile_photo']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profile_photo'].required = False
