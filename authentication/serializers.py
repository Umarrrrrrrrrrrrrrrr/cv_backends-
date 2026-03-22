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
    full_name = serializers.SerializerMethodField()
    profile_photo_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'full_name',
            'phone', 'location', 'bio', 'linkedin_url', 'website_url',
            'profile_photo', 'profile_photo_url',
            'is_active', 'is_verified', 'role',
            'is_staff', 'is_superuser',
            'last_login_at', 'created_at', 'updated_at',
        )
        read_only_fields = (
            'id', 'is_active', 'is_verified', 'is_staff', 'is_superuser',
            'last_login_at', 'created_at', 'updated_at',
        )

    def get_full_name(self, obj):
        if obj.first_name or obj.last_name:
            return f"{obj.first_name or ''} {obj.last_name or ''}".strip()
        return obj.username

    def get_profile_photo_url(self, obj):
        if obj.profile_photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_photo.url)
            return obj.profile_photo.url
        return None


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating profile - accepts full_name or first_name/last_name"""
    full_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    linkedin_url = serializers.URLField(required=False, allow_blank=True)
    website_url = serializers.URLField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'full_name',
            'username', 'phone', 'location', 'bio',
            'linkedin_url', 'website_url', 'profile_photo',
        )

    def validate_linkedin_url(self, value):
        return value.strip() if value else ''

    def validate_website_url(self, value):
        return value.strip() if value else ''

    def validate_username(self, value):
        user = self.instance
        if user and User.objects.filter(username=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value.strip()

    def update(self, instance, validated_data):
        full_name = validated_data.pop('full_name', None)
        if full_name:
            parts = full_name.strip().split(None, 1)
            instance.first_name = parts[0] if parts else ''
            instance.last_name = parts[1] if len(parts) > 1 else ''
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class AdminUserDetailSerializer(serializers.ModelSerializer):
    """Staff API: read user for list/detail."""

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'role',
            'phone', 'location', 'bio',
            'is_active', 'is_verified', 'is_staff', 'is_superuser',
            'last_login_at', 'created_at', 'updated_at',
        )


class AdminUserCreateSerializer(serializers.ModelSerializer):
    """Staff API: create user (superuser may set is_staff / is_superuser)."""
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            'email', 'username', 'password', 'password_confirm',
            'first_name', 'last_name', 'role', 'is_active', 'is_verified',
            'is_staff', 'is_superuser',
        )

    def validate_email(self, value):
        v = value.lower().strip()
        if User.objects.filter(email=v).exists():
            raise serializers.ValidationError('This email is already registered.')
        return v

    def validate_username(self, value):
        v = value.strip()
        if len(v) < 2:
            raise serializers.ValidationError('Username must be at least 2 characters.')
        if User.objects.filter(username=v).exists():
            raise serializers.ValidationError('This username is already taken.')
        return v

    def validate(self, attrs):
        request = self.context.get('request')
        if request and not request.user.is_superuser:
            attrs.pop('is_superuser', None)
            attrs.pop('is_staff', None)
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        attrs.pop('password_confirm', None)
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        email = validated_data.pop('email')
        username = validated_data.pop('username')
        user = User.objects.create_user(
            email=email,
            username=username,
            password=password,
        )
        for attr, value in validated_data.items():
            setattr(user, attr, value)
        user.save()
        return user


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """Staff API: update user; optional new password."""
    password = serializers.CharField(write_only=True, required=False, allow_blank=True, min_length=6)

    class Meta:
        model = User
        fields = (
            'email', 'username', 'first_name', 'last_name', 'role',
            'phone', 'location', 'bio',
            'is_active', 'is_verified', 'is_staff', 'is_superuser', 'password',
        )

    def validate_email(self, value):
        v = value.lower().strip()
        user = self.instance
        if User.objects.filter(email=v).exclude(pk=user.pk).exists():
            raise serializers.ValidationError('This email is already in use.')
        return v

    def validate_username(self, value):
        v = value.strip()
        user = self.instance
        if User.objects.filter(username=v).exclude(pk=user.pk).exists():
            raise serializers.ValidationError('This username is already taken.')
        return v

    def validate(self, attrs):
        request = self.context.get('request')
        if request and not request.user.is_superuser:
            attrs.pop('is_superuser', None)
            attrs.pop('is_staff', None)
        return attrs

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


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
