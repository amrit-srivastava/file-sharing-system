from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
import jwt
from datetime import datetime, timedelta

class OpsUserPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == 'ops'

class ClientUserPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == 'client'

@api_view(['POST'])
def client_signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save(user_type='client')
        verification_url = request.build_absolute_uri(
            reverse('verify-email', args=[str(user.verification_token)])
        )
        
        # Send verification email
        send_mail(
            'Verify your email',
            f'Click this link to verify your email: {verification_url}',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
        
        return Response({
            'message': 'User created successfully. Please check your email for verification.',
            'verification_url': verification_url
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def verify_email(request, token):
    try:
        user = User.objects.get(verification_token=token)
        user.email_verified = True
        user.save()
        return Response({'message': 'Email verified successfully'})
    except User.DoesNotExist:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated, OpsUserPermission])
def upload_file(request):
    if 'file' not in request.FILES:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    file = request.FILES['file']
    extension = file.name.split('.')[-1].lower()
    
    if extension not in ['pptx', 'docx', 'xlsx']:
        return Response({'error': 'Invalid file type'}, status=status.HTTP_400_BAD_REQUEST)
    
    file_obj = File.objects.create(
        file=file,
        uploaded_by=request.user
    )
    
    return Response({
        'message': 'File uploaded successfully',
        'file_id': file_obj.id
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated, ClientUserPermission])
def list_files(request):
    files = File.objects.all()
    serializer = FileSerializer(files, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated, ClientUserPermission])
def get_download_link(request, file_id):
    try:
        file = File.objects.get(id=file_id)
        
        # Generate encrypted download token
        payload = {
            'file_id': file_id,
            'user_id': request.user.id,
            'exp': datetime.utcnow() + timedelta(minutes=30)
        }
        
        encrypted_token = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm='HS256'
        )
        
        download_url = request.build_absolute_uri(
            reverse('download-file', args=[encrypted_token])
        )
        
        return Response({
            'download_link': download_url,
            'message': 'success'
        })
    except File.DoesNotExist:
        return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated, ClientUserPermission])
def download_file(request, token):
    try:
        # Decode and verify token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        
        if payload['user_id'] != request.user.id:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        file = File.objects.get(id=payload['file_id'])
        
        response = FileResponse(file.file, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{file.file.name}"'
        return response
    
    except (jwt.InvalidTokenError, File.DoesNotExist):
        return Response({'error': 'Invalid or expired link'}, status=status.HTTP_400_BAD_REQUEST)