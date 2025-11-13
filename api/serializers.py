from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *

# ===== USER SERIALIZER =====
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.CharField(write_only=True, required=False)  # Allow frontend to send role

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role']

    def create(self, validated_data):
        role = validated_data.pop('role', None)  # Remove role from user creation
        user = User.objects.create_user(**validated_data)

        # Create user profile with role if provided
        profile = UserProfile.objects.create(user=user)
        if role in ['student', 'teacher', 'parent']:
            profile.role = role
            profile.save()

            # Create role-specific profile
            if role == 'student':
                StudentProfile.objects.get_or_create(user=user)
            elif role == 'teacher':
                TeacherProfile.objects.get_or_create(user=user)
            elif role == 'parent':
                ParentProfile.objects.get_or_create(user=user)

        return user

# ===== USER PROFILE SERIALIZER =====
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'role', 'created_at']

# ===== STUDENT PROFILE =====
class StudentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = StudentProfile
        fields = ['id', 'user', 'grade', 'learning_style', 'total_points', 'current_tier', 'current_streak']

# ===== TEACHER PROFILE =====
class TeacherProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = TeacherProfile
        fields = ['id', 'user', 'qualification', 'experience_years', 'bio']

# ===== PARENT PROFILE =====
class ParentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ParentProfile
        fields = ['id', 'user', 'children']

# ===== SUBJECTS =====
class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'description', 'grade_level']

class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ['id', 'subject', 'number', 'title', 'description']

class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'chapter', 'title', 'description']

class MCQOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MCQOption
        fields = ['id', 'option_text', 'is_correct']

class QuestionAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionAnswer
        fields = ['id', 'correct_answer', 'explanation', 'key_points', 'common_mistakes']

class QuestionSerializer(serializers.ModelSerializer):
    options = MCQOptionSerializer(many=True, read_only=True)
    answer = QuestionAnswerSerializer(read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'topic', 'question_text', 'question_type', 'difficulty', 'marks', 'created_by', 'created_at', 'options', 'answer']

class QuizQuestionSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(read_only=True)

    class Meta:
        model = QuizQuestion
        fields = ['id', 'quiz', 'question', 'order']

class QuizSerializer(serializers.ModelSerializer):
    questions = QuizQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'chapter', 'time_limit', 'passing_percentage', 'created_by', 'created_at', 'questions']

class StudyMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyMaterial
        fields = ['id', 'topic', 'title', 'material_type', 'content', 'file', 'url', 'rating']

class StudentQuizAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentQuizAnswer
        fields = ['id', 'attempt', 'question', 'student_answer', 'ai_score', 'ai_feedback', 'is_correct']

class QuizAttemptSerializer(serializers.ModelSerializer):
    answers = StudentQuizAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = QuizAttempt
        fields = ['id', 'student', 'quiz', 'started_at', 'completed_at', 'score', 'answers']

class PerformanceAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceAnalytics
        fields = ['id', 'student', 'chapter', 'conceptual_understanding', 'application_level',
                  'problem_solving', 'consistency', 'creativity', 'critical_thinking', 'speed', 'accuracy']

class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ['id', 'name', 'icon', 'description', 'requirement']

class StudentBadgeSerializer(serializers.ModelSerializer):
    badge = BadgeSerializer(read_only=True)

    class Meta:
        model = StudentBadge
        fields = ['id', 'student', 'badge', 'earned_at']
