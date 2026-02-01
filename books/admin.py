from django.contrib import admin
from books.models import Book, Outline, Chapter


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'status_outline_notes', 'final_review_notes_status', 'created_at']
    list_filter = ['status', 'status_outline_notes', 'final_review_notes_status']
    search_fields = ['title']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Outline)
class OutlineAdmin(admin.ModelAdmin):
    list_display = ['book', 'created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ['book', 'chapter_number', 'title', 'chapter_notes_status', 'created_at']
    list_filter = ['chapter_notes_status', 'book']
    search_fields = ['title', 'book__title']
    readonly_fields = ['created_at', 'updated_at']
