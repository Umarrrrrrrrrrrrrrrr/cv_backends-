import secrets
import string
try:
    import requests  # type: ignore
except ImportError:
    requests = None
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from django.conf import settings
from .serializers import UserRegistrationSerializer, UserSerializer, LoginSerializer
from .models import User


def format_validation_errors(errors):
    """Format Django REST Framework validation errors into user-friendly messages"""
    formatted_errors = {}
    error_messages = []
    
    for field, field_errors in errors.items():
        # Get the first error message for each field
        if isinstance(field_errors, list) and len(field_errors) > 0:
            error_msg = str(field_errors[0])
            formatted_errors[field] = error_msg
            error_messages.append(f"{field.replace('_', ' ').title()}: {error_msg}")
        else:
            formatted_errors[field] = str(field_errors)
            error_messages.append(f"{field.replace('_', ' ').title()}: {str(field_errors)}")
    
    return {
        'field_errors': formatted_errors,
        'message': '; '.join(error_messages) if error_messages else 'Validation failed'
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Register a new user"""
    try:
        # Normalize request data to handle different field name variations
        data = request.data.copy()
        
        # Handle different field name variations from frontend
        if 'emailAddress' in data:
            data['email'] = data.pop('emailAddress')
        if 'Email' in data:
            data['email'] = data.pop('Email')
        if 'confirmPassword' in data:
            data['password2'] = data.pop('confirmPassword')
        if 'ConfirmPassword' in data:
            data['password2'] = data.pop('ConfirmPassword')
        
        serializer = UserRegistrationSerializer(data=data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'success': True,
                'message': 'User registered successfully',
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        
        # Format validation errors for user-friendly response
        formatted_errors = format_validation_errors(serializer.errors)
        
        # Print validation errors for debugging (only in development)
        if settings.DEBUG:
            print(f"\n{'='*50}")
            print("VALIDATION ERRORS:")
            print(serializer.errors)
            print(f"ORIGINAL REQUEST DATA: {request.data}")
            print(f"NORMALIZED DATA: {data}")
            print(f"{'='*50}\n")
        
        return Response({
            'success': False,
            'message': formatted_errors['message'],
            'errors': formatted_errors['field_errors']
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        import traceback
        import sys
        error_type = type(e).__name__
        error_message = str(e)
        error_traceback = traceback.format_exc()
        
        # Print to console for debugging
        print(f"\n{'='*50}")
        print(f"ERROR TYPE: {error_type}")
        print(f"ERROR MESSAGE: {error_message}")
        print(f"TRACEBACK:\n{error_traceback}")
        print(f"{'='*50}\n")
        
        # User-friendly error messages based on error type
        user_message = 'An unexpected error occurred. Please try again later.'
        
        if 'relation' in error_message.lower() and 'does not exist' in error_message.lower():
            user_message = 'Database error. Please contact support.'
        elif 'unique' in error_message.lower() or 'duplicate' in error_message.lower():
            user_message = 'This email or username is already registered.'
        elif 'connection' in error_message.lower():
            user_message = 'Unable to connect to database. Please try again later.'
        
        return Response({
            'success': False,
            'message': user_message,
            'error': error_message if settings.DEBUG else None,
            'error_type': error_type if settings.DEBUG else None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Login user and return JWT tokens"""
    try:
        # Normalize request data
        data = request.data.copy()
        if 'emailAddress' in data:
            data['email'] = data.pop('emailAddress')
        if 'Email' in data:
            data['email'] = data.pop('Email')
        
        serializer = LoginSerializer(data=data)
        
        if not serializer.is_valid():
            formatted_errors = format_validation_errors(serializer.errors)
            return Response({
                'success': False,
                'message': formatted_errors['message'],
                'errors': formatted_errors['field_errors']
            }, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        try:
            user = User.objects.get(email=email.lower().strip())
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Invalid email or password. Please check your credentials and try again.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Authenticate user
        user = authenticate(username=user.username, password=password)
        
        if user is None:
            return Response({
                'success': False,
                'message': 'Invalid email or password. Please check your credentials and try again.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_active:
            return Response({
                'success': False,
                'message': 'Your account has been deactivated. Please contact support.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Update last_login_at
        user.last_login = timezone.now()
        user.last_login_at = timezone.now()
        user.save(update_fields=['last_login', 'last_login_at'])
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'success': True,
            'message': 'Login successful',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        import traceback
        if settings.DEBUG:
            print(f"\n{'='*50}")
            print(f"LOGIN ERROR: {str(e)}")
            print(traceback.format_exc())
            print(f"{'='*50}\n")
        
        return Response({
            'success': False,
            'message': 'An error occurred during login. Please try again later.',
            'error': str(e) if settings.DEBUG else None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    """Get current user profile"""
    return Response({
        'success': True,
        'user': UserSerializer(request.user).data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def suggest_password(request):
    """Generate a secure password suggestion"""
    length = int(request.GET.get('length', 12))
    length = max(8, min(length, 32))  # Between 8 and 32 characters
    
    # Generate secure password with mix of characters
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    
    # Ensure at least one of each type
    if not any(c.islower() for c in password):
        password = password[:-1] + secrets.choice(string.ascii_lowercase)
    if not any(c.isupper() for c in password):
        password = password[:-1] + secrets.choice(string.ascii_uppercase)
    if not any(c.isdigit() for c in password):
        password = password[:-1] + secrets.choice(string.digits)
    
    return Response({
        'success': True,
        'password': password,
        'length': len(password),
        'strength': 'strong' if length >= 12 else 'medium'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def google_auth(request):
    """Handle Google OAuth authentication"""
    try:
        if requests is None:
            return Response({
                'success': False,
                'message': 'Google authentication is not available. Please install requests: pip install requests'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        access_token = request.data.get('access_token')
        
        if not access_token:
            return Response({
                'success': False,
                'message': 'Google access token is required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify token with Google
        google_user_info_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = requests.get(google_user_info_url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return Response({
                'success': False,
                'message': 'Invalid Google access token.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        google_data = response.json()
        email = google_data.get('email', '').lower().strip()
        first_name = google_data.get('given_name', '')
        last_name = google_data.get('family_name', '')
        google_id = google_data.get('id', '')
        picture = google_data.get('picture', '')
        
        if not email:
            return Response({
                'success': False,
                'message': 'Email not provided by Google.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user exists
        try:
            user = User.objects.get(email=email)
            # User exists, just login
            if not user.is_active:
                return Response({
                    'success': False,
                    'message': 'Your account has been deactivated.'
                }, status=status.HTTP_403_FORBIDDEN)
        except User.DoesNotExist:
            # Create new user
            username = email.split('@')[0]
            # Ensure username is unique
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            user = User.objects.create_user(
                email=email,
                username=username,
                password=None,  # No password for OAuth users
                first_name=first_name,
                last_name=last_name,
                is_verified=True,  # Google emails are verified
            )
            user.set_unusable_password()  # OAuth users don't need passwords
            user.save()
        
        # Update last login
        user.last_login = timezone.now()
        user.last_login_at = timezone.now()
        user.save(update_fields=['last_login', 'last_login_at'])
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'success': True,
            'message': 'Google authentication successful',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'google_data': {
                'id': google_id,
                'picture': picture
            }
        }, status=status.HTTP_200_OK)
    
    except requests.RequestException as e:
        return Response({
            'success': False,
            'message': 'Failed to verify Google token. Please try again.',
            'error': str(e) if settings.DEBUG else None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except Exception as e:
        import traceback
        if settings.DEBUG:
            print(f"\n{'='*50}")
            print(f"GOOGLE AUTH ERROR: {str(e)}")
            print(traceback.format_exc())
            print(f"{'='*50}\n")
        
        return Response({
            'success': False,
            'message': 'An error occurred during Google authentication. Please try again.',
            'error': str(e) if settings.DEBUG else None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
