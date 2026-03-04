from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration - handles both password2 and confirmPassword"""
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=6,
        error_messages={
            'min_length': 'Password must be at least 6 characters long.'
        }
    )
    password2 = serializers.CharField(write_only=True, required=False)
    confirmPassword = serializers.CharField(write_only=True, required=False)
    role = serializers.CharField(max_length=50, required=False, default='user')

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password2', 'confirmPassword', 'role')
        extra_kwargs = {
            'username': {
                'required': True,
                'error_messages': {
                    'required': 'Username is required.',
                    'invalid': 'Please enter a valid username.'
                }
            },
            'email': {
                'required': True,
                'error_messages': {
                    'required': 'Email address is required.',
                    'invalid': 'Please enter a valid email address.',
                    'unique': 'This email is already registered.'
                }
            },
        }

    def validate_email(self, value):
        """Validate email format and uniqueness"""
        value = value.lower().strip()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered. Please use a different email or try logging in.")
        return value
    
    def validate_username(self, value):
        """Validate username format and uniqueness"""
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("Username must be at least 2 characters long.")
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken. Please choose a different one.")
        return value
    
    def validate(self, attrs):
        # Handle both password2 and confirmPassword field names
        password2 = attrs.get('password2') or attrs.get('confirmPassword')
        
        # If password confirmation is not provided, auto-confirm it (for password managers)
        if not password2:
            # Auto-confirm password for password manager compatibility
            attrs['password2'] = attrs['password']
        else:
            if attrs['password'] != password2:
                raise serializers.ValidationError({
                    "password": "Passwords do not match. Please make sure both password fields are the same."
                })
        
        # Remove the alternate field name if present
        if 'confirmPassword' in attrs:
            attrs['password2'] = attrs.pop('confirmPassword')
        
        return attrs

    def create(self, validated_data):
        # Remove password confirmation field
        validated_data.pop('password2', None)
        validated_data.pop('confirmPassword', None)
        
        password = validated_data.pop('password')
        role = validated_data.pop('role', 'user')
        
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=password,
        )
        # Set role after user creation
        user.role = role
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user data"""
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'is_active', 'is_verified', 'role', 
                  'last_login_at', 'created_at', 'updated_at')
        read_only_fields = ('id', 'is_active', 'is_verified', 'last_login_at', 
                          'created_at', 'updated_at')


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    email = serializers.EmailField(
        required=True,
        error_messages={
            'required': 'Email address is required.',
            'invalid': 'Please enter a valid email address.'
        }
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        error_messages={
            'required': 'Password is required.',
            'blank': 'Password cannot be empty.'
        }
    )
