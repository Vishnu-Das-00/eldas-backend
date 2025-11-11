from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'subjects', SubjectViewSet)
router.register(r'chapters', ChapterViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'quizzes', QuizViewSet)
router.register(r'quiz-attempts', QuizAttemptViewSet, basename='quiz-attempt')
router.register(r'performance', PerformanceAnalyticsViewSet, basename='performance')
router.register(r'badges', BadgeViewSet, basename='badge')

urlpatterns = [
    # Authentication
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/select-role/', SelectRoleView.as_view(), name='select-role'),
    path('auth/me/', CurrentUserView.as_view(), name='current-user'),
    
    # Student
    path('student/dashboard/', StudentDashboardView.as_view(), name='student-dashboard'),
    
    # Teacher
    path('teacher/dashboard/', TeacherDashboardView.as_view(), name='teacher-dashboard'),
    path('teacher/create-question/', CreateQuestionView.as_view(), name='create-question'),
    path('teacher/generate-questions/', GenerateQuestionsView.as_view(), name='generate-questions'),
    
    # Parent
    path('parent/dashboard/', ParentDashboardView.as_view(), name='parent-dashboard'),
    
    # Router
    path('', include(router.urls)),
]
