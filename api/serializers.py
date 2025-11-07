from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer as JwtTokenObtainPairSerializers
from accounts.models import UserProfile
from courses.models import Course, Lesson, Module, Enrollment
from django.contrib.auth import get_user_model

User = get_user_model()

class TokenObtainPairSerializer(JwtTokenObtainPairSerializers):
    username_field = User.USERNAME_FIELD

    def validate(self, attrs):
        data = super().validate(attrs)
        # Add extra info to JWT response
        data.update({
            "id": self.user.id,
            "email": self.user.email,
            "role": self.user.role,
        })
        return data


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    username = None

    class Meta:
        model = User
        fields = ("email", "password", "role", "bio", "profile_picture",)

    def validate_email(self, value):
        """
        Ensure the email is unique before creating the user.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value


    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            role =validated_data.get("role", User.Roles.STUDENT),
            bio=validated_data.get("bio", ""),
            profile_picture=validated_data.get("profile_picture"),
        )
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            'phone_number',
            'address',
            'city',
            'country',
            'date_of_birth',
            'linkedin_url',
            'github_url',
        )

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=False)
    
    class Meta:
        model = User
        fields = (
            "id", 
            "email", 
            "first_name", 
            "last_name", 
            "role", 
            "is_active", 
            "date_joined",
            "bio",
            "profile_picture",
            "profile",
        )
        
    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update or create profile
        if profile_data:
            profile, created = UserProfile.objects.get_or_create(user=instance)
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ("id", "module", "title", "content", "video_url", "order",)
    
class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    class Meta:
        model = Module
        fields = ("id", "course", "title", "order", "lessons",)


class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    instructor = serializers.StringRelatedField()
    class Meta:
        model = Course
        fields = ("id", "title", "slug", "description", "instructor", "published", "modules",)

class EnrollmentSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField()
    course = serializers.StringRelatedField()    
    class Meta:
        model = Enrollment
        fields = ('id', 'student', 'course', 'progress', 'completed',)
