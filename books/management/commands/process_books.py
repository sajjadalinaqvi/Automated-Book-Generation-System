from django.core.management.base import BaseCommand
from books.models import Book
from books.services.outline_service import OutlineService
from books.services.chapter_service import ChapterService
from books.services.compilation_service import CompilationService


class Command(BaseCommand):
    help = 'Process book generation workflow'
    
    def add_arguments(self, parser):
        parser.add_argument('--book-id', type=int, help='Process specific book ID')
        parser.add_argument('--stage', choices=['outline', 'chapters', 'compile'], help='Process specific stage')
    
    def handle(self, *args, **options):
        book_id = options.get('book_id')
        stage = options.get('stage')
        
        if book_id:
            books = Book.objects.filter(id=book_id)
        else:
            books = Book.objects.exclude(status='completed')
        
        for book in books:
            self.process_book(book, stage)
    
    def process_book(self, book, stage=None):
        self.stdout.write(f"Processing book: {book.title}")
        
        # Stage 1: Outline Generation
        if not stage or stage == 'outline':
            if book.status == 'outline':
                self.process_outline_stage(book)
        
        # Stage 2: Chapter Generation
        if not stage or stage == 'chapters':
            if book.status == 'chapters':
                self.process_chapter_stage(book)
        
        # Stage 3: Compilation
        if not stage or stage == 'compile':
            if book.status == 'compilation':
                self.process_compilation_stage(book)
    
    def process_outline_stage(self, book):
        outline_service = OutlineService()
        
        if outline_service.can_generate_outline(book) and not hasattr(book, 'outline'):
            try:
                outline = outline_service.generate_outline(book)
                self.stdout.write(f"Generated outline for: {book.title}")
            except Exception as e:
                self.stdout.write(f"Error generating outline: {e}")
        
        if outline_service.can_proceed_to_chapters(book):
            book.status = 'chapters'
            book.save()
            self.stdout.write(f"Advanced {book.title} to chapter generation")
    
    def process_chapter_stage(self, book):
        chapter_service = ChapterService()
        
        if chapter_service.all_chapters_approved(book):
            book.status = 'compilation'
            book.save()
            self.stdout.write(f"Advanced {book.title} to compilation stage")
    
    def process_compilation_stage(self, book):
        compilation_service = CompilationService()
        
        if compilation_service.can_compile_book(book):
            try:
                filepath = compilation_service.compile_book_to_docx(book)
                self.stdout.write(f"Compiled book: {filepath}")
            except Exception as e:
                self.stdout.write(f"Error compiling book: {e}")