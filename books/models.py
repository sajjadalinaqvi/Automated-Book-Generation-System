from django.db import models
from django.contrib.auth.models import User


class Book(models.Model):
    STATUS_CHOICES = [
        ('outline', 'Outline Stage'),
        ('chapters', 'Chapter Generation'),
        ('compilation', 'Final Compilation'),
        ('completed', 'Completed'),
    ]
    
    OUTLINE_STATUS_CHOICES = [
        ('yes', 'Yes - Wait for notes'),
        ('no_notes_needed', 'No notes needed - Proceed'),
        ('no', 'No - Pause'),
        ('', 'Empty - Pause'),
    ]
    
    REVIEW_STATUS_CHOICES = [
        ('yes', 'Yes - Wait for notes'),
        ('no_notes_needed', 'No notes needed - Proceed'),
        ('no', 'No - Pause'),
        ('', 'Empty - Pause'),
    ]
    
    title = models.CharField(max_length=255)
    notes_on_outline_before = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='outline')
    status_outline_notes = models.CharField(max_length=20, choices=OUTLINE_STATUS_CHOICES, default='')
    final_review_notes_status = models.CharField(max_length=20, choices=REVIEW_STATUS_CHOICES, default='')
    book_output_status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title


class Outline(models.Model):
    book = models.OneToOneField(Book, on_delete=models.CASCADE, related_name='outline')
    content = models.TextField()
    post_outline_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Outline for {self.book.title}"


class Chapter(models.Model):
    CHAPTER_STATUS_CHOICES = [
        ('yes', 'Yes - Wait for notes'),
        ('no_notes_needed', 'No notes needed - Proceed'),
        ('no', 'No - Pause'),
        ('', 'Empty - Pause'),
    ]
    
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='chapters')
    chapter_number = models.IntegerField()
    title = models.CharField(max_length=255)
    content = models.TextField()
    summary = models.TextField()
    notes = models.TextField(blank=True)
    chapter_notes_status = models.CharField(max_length=20, choices=CHAPTER_STATUS_CHOICES, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['book', 'chapter_number']
        ordering = ['chapter_number']
    
    def __str__(self):
        return f"Chapter {self.chapter_number}: {self.title}"
