from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    # Auth Views
    UserViewSet,
    client_signup,
    verify_email,
    
    # File Management Views
    FileViewSet,
    upload_file,
    download_file,
    get_download_link,
    list_files,
    
    # Optional: Additional Views
    UserProfileViewSet,
    FileStatisticsViewSet,
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'files', FileViewSet)
router.register(r'profiles', UserProfileViewSet)
router.register(r'statistics', FileStatisticsViewSet)

app_name = 'file_management'

urlpatterns = [
    # Authentication Endpoints
    path('auth/signup/', client_signup, name='client-signup'),
    path('auth/verify-email/<str:token>/', verify_email, name='verify-email'),
    
    # File Management Endpoints
    path('files/upload/', upload_file, name='file-upload'),
    path('files/download/<str:file_id>/', get_download_link, name='get-download-link'),
    path('files/download/secure/<str:token>/', download_file, name='download-file'),
    path('files/list/', list_files, name='list-files'),
    
    # Optional: Additional Endpoints
    path('users/profile/', 'user_profile', name='user-profile'),
    path('files/statistics/', 'file_statistics', name='file-statistics'),
    
    # Optional: Batch Operations
    path('files/batch-upload/', 'batch_upload', name='batch-upload'),
    path('files/batch-delete/', 'batch_delete', name='batch-delete'),
]

# Include router URLs
urlpatterns += router.urls