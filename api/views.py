from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from .models import *
from .serializers import *
import google.generativeai as genai
from decouple import config

genai.configure(api_key=config('GEMINI_API_KEY', default=''))

# ===== AUTHENTICATION =====
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        UserProfile.objects.create(user=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]

class SelectRoleView(generics.UpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user.profile
    
    def update(self, request, *args, **kwargs):
        profile = self.get_object()
        role = request.data.get('role')
        
        if role in ['student', 'teacher', 'parent']:
            profile.role = role
            profile.save()
            
            if role == 'student':
                StudentProfile.objects.get_or_create(user=request.user)
            elif role == 'teacher':
                TeacherProfile.objects.get_or_create(user=request.user)
            elif role == 'parent':
                ParentProfile.objects.get_or_create(user=request.user)
            
            return Response({'message': f'Role set to {role}'}, status=status.HTTP_200_OK)
        
        return Response({'error': 'Invalid role'}, status=status.HTTP_400_BAD_REQUEST)

class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user.profile

# ===== STUDENT ENDPOINTS =====
class StudentDashboardView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StudentProfileSerializer
    
    def get_object(self):
        return self.request.user.student_profile

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]

class ChapterViewSet(viewsets.ModelViewSet):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer
    permission_classes = [IsAuthenticated]

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]

class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def start_quiz(self, request, pk=None):
        quiz = self.get_object()
        student = request.user.student_profile
        
        attempt = QuizAttempt.objects.create(
            student=student,
            quiz=quiz
        )
        
        return Response({
            'attempt_id': attempt.id,
            'quiz_id': quiz.id,
            'time_limit': quiz.time_limit
        }, status=status.HTTP_201_CREATED)

class QuizAttemptViewSet(viewsets.ModelViewSet):
    serializer_class = QuizAttemptSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return QuizAttempt.objects.filter(student__user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def submit_answer(self, request, pk=None):
        attempt = self.get_object()
        question_id = request.data.get('question_id')
        student_answer = request.data.get('answer')
        
        question = Question.objects.get(id=question_id)
        answer = question.answer
        
        # AI Evaluation using Gemini
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"""
        Question: {question.question_text}
        Model Answer: {answer.correct_answer}
        Student Answer: {student_answer}
        
        Evaluate the student's answer and provide:
        1. A score from 0-100
        2. Feedback
        3. Whether it's correct (true/false)
        
        Respond in JSON format:
        {{"score": 85, "feedback": "Good answer", "is_correct": true}}
        """
        
        response = model.generate_content(prompt)
        import json
        try:
            result = json.loads(response.text)
        except:
            result = {'score': 50, 'feedback': 'Answer evaluated', 'is_correct': False}
        
        quiz_answer = StudentQuizAnswer.objects.create(
            attempt=attempt,
            question=question,
            student_answer=student_answer,
            ai_score=result.get('score', 50),
            ai_feedback=result.get('feedback', ''),
            is_correct=result.get('is_correct', False)
        )
        
        return Response(result, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def complete_quiz(self, request, pk=None):
        from django.utils import timezone
        attempt = self.get_object()
        
        answers = attempt.answers.all()
        total_score = sum(a.ai_score or 0 for a in answers)
        total_marks = attempt.quiz.questions.count()
        percentage = (total_score / (total_marks * 100)) * 100 if total_marks > 0 else 0
        
        attempt.score = percentage
        attempt.completed_at = timezone.now()
        attempt.save()
        
        return Response({
            'score': attempt.score,
            'total_questions': total_marks,
            'passed': percentage >= attempt.quiz.passing_percentage
        }, status=status.HTTP_200_OK)

class PerformanceAnalyticsViewSet(viewsets.ModelViewSet):
    serializer_class = PerformanceAnalyticsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PerformanceAnalytics.objects.filter(student__user=self.request.user)

class BadgeViewSet(viewsets.ModelViewSet):
    serializer_class = BadgeSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def my_badges(self, request):
        badges = StudentBadge.objects.filter(student__user=request.user)
        serializer = StudentBadgeSerializer(badges, many=True)
        return Response(serializer.data)

# ===== TEACHER ENDPOINTS =====
class TeacherDashboardView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeacherProfileSerializer
    
    def get_object(self):
        return self.request.user.teacher_profile

class CreateQuestionView(generics.CreateAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user.teacher_profile)

class GenerateQuestionsView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        # AI generates questions from textbook image
        model = genai.GenerativeModel('gemini-pro')
        
        text_content = request.data.get('content', '')
        difficulty = request.data.get('difficulty', 'medium')
        
        prompt = f"""
        Generate 5 multiple-choice questions from this content:
        
        {text_content}
        
        Difficulty: {difficulty}
        
        For each question provide:
        - Question text
        - 4 options (A, B, C, D)
        - Correct answer
        - Explanation
        
        Return as JSON array.
        """
        
        response = model.generate_content(prompt)
        import json
        try:
            questions = json.loads(response.text)
        except:
            questions = []
        
        return Response(questions, status=status.HTTP_201_CREATED)

# ===== PARENT ENDPOINTS =====
class ParentDashboardView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ParentProfileSerializer
    
    def get_object(self):
        return self.request.user.parent_profile
