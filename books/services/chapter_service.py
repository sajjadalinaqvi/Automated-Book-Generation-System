from books.models import Book, Chapter
from books.services.groq_service import GroqService
from books.services.pinecone_service import PineconeService


class ChapterService:
    def __init__(self):
        self.groq_service = GroqService()
        self.pinecone_service = PineconeService()
    
    def can_generate_chapters(self, book):
        """Check if chapter generation can start"""
        # Allow chapter generation if outline status is approved, even without outline content
        return book.status_outline_notes in ['no_notes_needed', 'yes']
    
    def generate_next_chapter(self, book, chapter_title, chapter_number):
        """Generate next chapter with RAG context"""
        if not self.can_generate_chapters(book):
            raise ValueError("Cannot generate chapters: outline not approved")
        
        # Get previous chapter summaries for context
        previous_summaries = self._get_previous_summaries(book, chapter_number)
        
        # Optional: Get research context from Pinecone
        research_context = self._get_research_context(book.id, chapter_number)
        
        # Generate chapter content
        chapter_content = self.groq_service.generate_chapter(
            chapter_title, 
            chapter_number, 
            previous_summaries,
            research_context
        )
        
        # Generate chapter summary
        chapter_summary = self.groq_service.generate_chapter_summary(chapter_content)
        
        # Create chapter record
        chapter = Chapter.objects.create(
            book=book,
            chapter_number=chapter_number,
            title=chapter_title,
            content=chapter_content,
            summary=chapter_summary
        )
        
        # Store summary in Pinecone for future RAG
        self.pinecone_service.embed_chapter_summary(
            book.id, 
            chapter_number, 
            chapter_summary
        )
        
        return chapter
    
    def can_proceed_chapter(self, chapter):
        """Check if chapter can proceed based on chapter_notes_status"""
        if chapter.chapter_notes_status == 'no_notes_needed':
            return True
        elif chapter.chapter_notes_status == 'yes' and chapter.notes:
            return True
        return False
    
    def all_chapters_approved(self, book):
        """Check if all chapters are approved for final compilation"""
        chapters = book.chapters.all()
        if not chapters:
            return False
        
        for chapter in chapters:
            if not self.can_proceed_chapter(chapter):
                return False
        return True
    
    def _get_previous_summaries(self, book, current_chapter):
        """Get summaries of all previous chapters"""
        previous_chapters = book.chapters.filter(
            chapter_number__lt=current_chapter
        ).order_by('chapter_number')
        
        return [chapter.summary for chapter in previous_chapters]
    
    def _get_research_context(self, book_id, chapter_number):
        """Optional: Retrieve relevant research from Pinecone"""
        try:
            summaries = self.pinecone_service.retrieve_previous_summaries(
                book_id, 
                chapter_number
            )
            return "\n".join(summaries)
        except:
            return ""