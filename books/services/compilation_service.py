from books.models import Book
from docx import Document
import os
from django.conf import settings


class CompilationService:
    
    def can_compile_book(self, book):
        """Check if book can be compiled based on final_review_notes_status"""
        if book.final_review_notes_status == 'no_notes_needed':
            return True
        elif book.final_review_notes_status == 'yes':
            return True
        # Allow compilation if no final review status is set but chapters exist
        elif book.chapters.exists():
            return True
        return False
    
    def compile_book_to_docx(self, book):
        """Compile all approved chapters into a .docx file"""
        if not self.can_compile_book(book):
            raise ValueError("Cannot compile: final review not approved")
        
        doc = Document()
        
        # Add title
        title = doc.add_heading(book.title, 0)
        title.alignment = 1  # Center alignment
        
        # Add outline if exists
        if hasattr(book, 'outline') and book.outline.content:
            doc.add_heading('Outline', level=1)
            doc.add_paragraph(book.outline.content)
            doc.add_page_break()
        
        # Add chapters
        chapters = book.chapters.order_by('chapter_number')
        for chapter in chapters:
            doc.add_heading(f"Chapter {chapter.chapter_number}: {chapter.title}", level=1)
            doc.add_paragraph(chapter.content)
            doc.add_page_break()
        
        # Save file
        filename = f"{book.title.replace(' ', '_')}_book.docx"
        filepath = os.path.join(settings.BASE_DIR, 'media', 'books', filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        doc.save(filepath)
        
        # Update book status
        book.book_output_status = 'completed'
        book.status = 'completed'
        book.save()
        
        return filepath
    
    def compile_book_to_txt(self, book):
        """Compile all approved chapters into a .txt file"""
        if not self.can_compile_book(book):
            raise ValueError("Cannot compile: final review not approved")
        
        content = []
        
        # Add title
        content.append(f"{book.title}\n{'=' * len(book.title)}\n")
        
        # Add outline if exists
        if hasattr(book, 'outline') and book.outline.content:
            content.append("OUTLINE\n-------\n")
            content.append(f"{book.outline.content}\n\n")
        
        # Add chapters
        chapters = book.chapters.order_by('chapter_number')
        for chapter in chapters:
            content.append(f"CHAPTER {chapter.chapter_number}: {chapter.title.upper()}\n")
            content.append("-" * 50 + "\n")
            content.append(f"{chapter.content}\n\n")
        
        # Save file
        filename = f"{book.title.replace(' ', '_')}_book.txt"
        filepath = os.path.join(settings.BASE_DIR, 'media', 'books', filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
        
        # Update book status
        book.book_output_status = 'completed'
        book.status = 'completed'
        book.save()
        
        return filepath