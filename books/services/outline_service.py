from books.models import Book, Outline
from books.services.groq_service import GroqService


class OutlineService:
    def __init__(self):
        self.groq_service = GroqService()
    
    def can_generate_outline(self, book):
        """Check if outline can be generated based on gating logic"""
        return bool(book.notes_on_outline_before.strip())
    
    def generate_outline(self, book):
        """Generate outline only if notes_on_outline_before exists"""
        if not self.can_generate_outline(book):
            raise ValueError("Cannot generate outline: notes_on_outline_before is required")
        
        outline_content = self.groq_service.generate_outline(
            book.title, 
            book.notes_on_outline_before
        )
        
        outline, created = Outline.objects.get_or_create(
            book=book,
            defaults={'content': outline_content}
        )
        
        if not created:
            outline.content = outline_content
            outline.save()
        
        return outline
    
    def can_proceed_to_chapters(self, book):
        """Check if can proceed to chapter generation based on status_outline_notes"""
        if book.status_outline_notes == 'no_notes_needed':
            return True
        elif book.status_outline_notes == 'yes' and hasattr(book, 'outline') and book.outline.post_outline_notes:
            return True
        return False
    
    def regenerate_outline(self, book, post_outline_notes):
        """Regenerate outline with additional notes"""
        if not hasattr(book, 'outline'):
            raise ValueError("No existing outline to regenerate")
        
        combined_notes = f"{book.notes_on_outline_before}\n\nAdditional notes:\n{post_outline_notes}"
        
        new_content = self.groq_service.generate_outline(book.title, combined_notes)
        
        book.outline.content = new_content
        book.outline.post_outline_notes = post_outline_notes
        book.outline.save()
        
        return book.outline