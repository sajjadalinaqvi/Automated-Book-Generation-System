from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import FileResponse
from books.models import Book, Outline, Chapter
from books.serializers import BookSerializer, OutlineSerializer, ChapterSerializer, BookCreateSerializer
from books.services.outline_service import OutlineService
from books.services.chapter_service import ChapterService
from books.services.compilation_service import CompilationService


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    
    def get_serializer_class(self):
        if self.action == 'create':
            return BookCreateSerializer
        return BookSerializer
    
    @action(detail=True, methods=['post'])
    def generate_outline(self, request, pk=None):
        book = self.get_object()
        outline_service = OutlineService()
        
        try:
            outline = outline_service.generate_outline(book)
            return Response(OutlineSerializer(outline).data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'Unexpected error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def update_outline_status(self, request, pk=None):
        book = self.get_object()
        book.status_outline_notes = request.data.get('status_outline_notes', '')
        book.save()
        return Response(BookSerializer(book).data)
    
    @action(detail=True, methods=['post'])
    def generate_chapter(self, request, pk=None):
        book = self.get_object()
        chapter_service = ChapterService()
        
        chapter_title = request.data.get('chapter_title')
        chapter_number = request.data.get('chapter_number')
        
        if not chapter_title or not chapter_number:
            return Response({'error': 'chapter_title and chapter_number are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            chapter = chapter_service.generate_next_chapter(book, chapter_title, chapter_number)
            return Response(ChapterSerializer(chapter).data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'Unexpected error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def compile_book(self, request, pk=None):
        book = self.get_object()
        compilation_service = CompilationService()
        output_format = request.data.get('format', 'docx')
        
        try:
            if output_format == 'txt':
                filepath = compilation_service.compile_book_to_txt(book)
            else:
                filepath = compilation_service.compile_book_to_docx(book)
            
            return FileResponse(
                open(filepath, 'rb'),
                as_attachment=True,
                filename=filepath.split('/')[-1]
            )
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ChapterViewSet(viewsets.ModelViewSet):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        chapter = self.get_object()
        chapter.chapter_notes_status = request.data.get('chapter_notes_status', '')
        chapter.notes = request.data.get('notes', '')
        chapter.save()
        return Response(ChapterSerializer(chapter).data)
