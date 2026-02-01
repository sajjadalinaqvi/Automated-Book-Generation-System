from rest_framework import serializers
from books.models import Book, Outline, Chapter


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


class OutlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Outline
        fields = '__all__'


class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = '__all__'


class BookCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['title', 'notes_on_outline_before']
    
    def validate_notes_on_outline_before(self, value):
        if not value.strip():
            raise serializers.ValidationError("notes_on_outline_before is required")
        return value