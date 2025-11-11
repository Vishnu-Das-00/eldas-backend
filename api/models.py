from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# ===== 1. USER PROFILE =====
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('parent', 'Parent'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"

# ===== 2. STUDENT PROFILE =====
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    grade = models.CharField(max_length=10, blank=True)
    learning_style = models.CharField(max_length=50, blank=True)
    total_points = models.IntegerField(default=0)
    current_tier = models.CharField(max_length=20, default='Bronze')
    current_streak = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Student: {self.user.username}"

# ===== 3. TEACHER PROFILE =====
class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    qualification = models.CharField(max_length=100, blank=True)
    experience_years = models.IntegerField(default=0)
    bio = models.TextField(blank=True)
    
    def __str__(self):
        return f"Teacher: {self.user.username}"

# ===== 4. PARENT PROFILE =====
class ParentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_profile')
    children = models.ManyToManyField(StudentProfile, blank=True)
    
    def __str__(self):
        return f"Parent: {self.user.username}"

# ===== 5. SUBJECT =====
class Subject(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    grade_level = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return self.name

# ===== 6. CHAPTER =====
class Chapter(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='chapters')
    number = models.IntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    class Meta:
        ordering = ['number']
    
    def __str__(self):
        return f"{self.subject.name} - Ch {self.number}: {self.title}"

# ===== 7. TOPIC =====
class Topic(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='topics')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.chapter.title} - {self.title}"

# ===== 8. QUESTION =====
class Question(models.Model):
    TYPES = [('mcq', 'Multiple Choice'), ('short', 'Short Answer'), ('essay', 'Essay')]
    
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=10, choices=TYPES)
    difficulty = models.CharField(max_length=10, choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')])
    marks = models.IntegerField(default=1)
    created_by = models.ForeignKey(TeacherProfile, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.question_text[:100]

# ===== 9. MCQ OPTION =====
class MCQOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    option_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return self.option_text[:50]

# ===== 10. QUESTION ANSWER =====
class QuestionAnswer(models.Model):
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='answer')
    correct_answer = models.TextField()
    explanation = models.TextField()
    key_points = models.TextField(blank=True)
    common_mistakes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Answer: {self.question.question_text[:50]}"

# ===== 11. QUIZ =====
class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='quizzes')
    time_limit = models.IntegerField(help_text="Minutes")
    passing_percentage = models.IntegerField(default=50)
    created_by = models.ForeignKey(TeacherProfile, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

# ===== 12. QUIZ QUESTION =====
class QuizQuestion(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    order = models.IntegerField()
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.quiz.title} - Q{self.order}"

# ===== 13. QUIZ ATTEMPT =====
class QuizAttempt(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.student.user.username} - {self.quiz.title}"

# ===== 14. STUDENT QUIZ ANSWER =====
class StudentQuizAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    student_answer = models.TextField()
    ai_score = models.FloatField(null=True, blank=True)
    ai_feedback = models.TextField(blank=True)
    is_correct = models.BooleanField(null=True, blank=True)
    
    def __str__(self):
        return f"Answer - {self.attempt.student.user.username}"

# ===== 15. STUDY MATERIAL =====
class StudyMaterial(models.Model):
    TYPES = [('note', 'Note'), ('video', 'Video'), ('image', 'Image'), ('pdf', 'PDF'), ('link', 'Link')]
    
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=200)
    material_type = models.CharField(max_length=20, choices=TYPES)
    content = models.TextField(blank=True)
    file = models.FileField(upload_to='materials/', null=True, blank=True)
    url = models.URLField(blank=True)
    rating = models.FloatField(default=5.0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    
    def __str__(self):
        return f"{self.title} - {self.material_type}"

# ===== PERFORMANCE ANALYTICS =====
class PerformanceAnalytics(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='performance')
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    conceptual_understanding = models.FloatField(default=0)
    application_level = models.FloatField(default=0)
    problem_solving = models.FloatField(default=0)
    consistency = models.FloatField(default=0)
    creativity = models.FloatField(default=0)
    critical_thinking = models.FloatField(default=0)
    speed = models.FloatField(default=0)
    accuracy = models.FloatField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student.user.username} - {self.chapter.title}"

# ===== BADGE =====
class Badge(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50)
    description = models.TextField()
    requirement = models.TextField()
    
    def __str__(self):
        return self.name

# ===== STUDENT BADGE =====
class StudentBadge(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('student', 'badge')
    
    def __str__(self):
        return f"{self.student.user.username} - {self.badge.name}"
