from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),  
    path('', views.home, name='home'),  
    path('upload-resume/', views.upload_resume, name='upload_resume'),
    path('update-resume/', views.update_resume, name='update_resume'),
    path('delete-resume/', views.delete_resume, name='delete_resume'),
    path('download-resume/', views.download_resume, name='download_resume'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('delete-account/', views.delete_account, name='delete_account'),
]
