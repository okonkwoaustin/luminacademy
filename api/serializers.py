from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer as JwtTokenObtainPairSerializers
from accounts.models import UserProfile
from courses.models import Course, Lesson, Module, Enrollment
from django.contrib.auth import authenticate
from dj_rest_auth.serializers import LoginSerializer
from dj_rest_auth.registration.serializers import RegisterSerializer
from assessments.models import Quiz, Question, Submission
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

class CustomRegisterSerializer(RegisterSerializer):
    username = None 
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True, max_length=30)
    last_name = serializers.CharField(required = True, max_length=30)
    phone_number = serializers.CharField(required=False, max_length=20)
    role = serializers.ChoiceField(choices=User.Roles.choices, default=User.Roles.STUDENT)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def validate_phone_number(self, value):
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("An account with this phone number already exists.")
        return value

    def get_cleaned_data(self):
        """Override to clean only fields that exist."""
        return {
            'email': self.validated_data.get('email', ''),
            'password1': self.validated_data.get('password1', ''),
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'phone_number': self.validated_data.get('phone_number', ''),
            'role': self.validated_data.get('role', User.Roles.STUDENT)
        }
    
    def save(self, request):
        user = User.objects.create_user(
            email=self.validated_data["email"],
            first_name=self.validated_data["first_name"],
            last_name=self.validated_data["last_name"],
            password=self.validated_data["password1"],
            phone_number=self.validated_data.get("phone_number", ""),
            role =self.validated_data.get("role", User.Roles.STUDENT),
        )
        return user

class CustomLoginSerializer(LoginSerializer):
    """Custom login serializer that uses email field instead of username."""
    username = None

    # Make email or phone field required
    email_or_phone = serializers.CharField(required=True)

    def authenticate(self, **kwargs):
        email_or_phone = self.validated_data.get('email_or_phone')
        password = self.validated_data.get('password')

        user = authenticate(
            self.context['request'],
            username=email_or_phone,
            password=password,
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
    class Meta:
        model = Course
        fields = (
            "id", 
            "title", 
            "slug", 
            "description", 
            "category", 
            "price", 
            "owner", 
            "published", 
            "modules",
    )
    read_only_fields = ['owner']
        
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['owner'] = user
        return super().create(validated_data)

class EnrollmentSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField()
    course = serializers.StringRelatedField()    
    class Meta:
        model = Enrollment
        fields = ('id', 'student', 'course', 'progress', 'completed',)


class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ('id', 'course', 'title', 'description', 'duration', 'total_marks', 'created_at', 'updated_at',)

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = (
            'id', 
            'quiz', 
            'text', 
            'option_a', 
            'option_b', 
            'option_c', 
            'option_d', 
            'correct_answer', 
            'marks', 
            'created_at', 
            'updated_at',
        )

class SubmissionSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField()
    quiz = serializers.StringRelatedField()
    class Meta:
        model = Submission
        fields = (
            'id', 
            'quiz', 
            'student', 
            'total_marks_obtained', 
            'submitted_at', 
            'is_graded',
        )