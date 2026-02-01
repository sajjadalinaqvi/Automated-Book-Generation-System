from groq import Groq
from django.conf import settings


class GroqService:
    def __init__(self):
        try:
            self.client = Groq(api_key=settings.GROQ_API_KEY)
            self.model = "llama3-70b-8192"
        except Exception as e:
            print(f"Groq initialization error: {e}")
            self.client = None
    
    def generate_outline(self, title, notes_before):
        if not self.client:
            return self._mock_outline(title, notes_before)
            
        prompt = f"""
You are a professional book outline generator. Create a detailed chapter-by-chapter outline for a book titled "{title}".

Special instructions from the author:
{notes_before}

Generate a structured outline with:
- Chapter numbers and titles
- Brief description of each chapter's content
- Logical flow between chapters

Format as a clear, numbered list.
"""
        
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Groq API error: {e}")
            return self._mock_outline(title, notes_before)
    
    def generate_chapter(self, chapter_title, chapter_number, previous_summaries, research_context=""):
        if not self.client:
            return self._mock_chapter(chapter_title, chapter_number, previous_summaries)
            
        context = "\n".join([f"Chapter {i+1} Summary: {summary}" for i, summary in enumerate(previous_summaries)])
        research_section = "Research context:\n" + research_context if research_context else ""
        
        prompt = f"""
You are writing Chapter {chapter_number}: {chapter_title}

Previous chapters context:
{context}

{research_section}

Write a comprehensive chapter that:
- Flows naturally from previous chapters
- Maintains consistency with the overall narrative
- Is approximately 2000-3000 words
- Has clear structure and engaging content

Write the full chapter content:
"""
        
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0.7,
                max_tokens=4000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Groq API error: {e}")
            return self._mock_chapter(chapter_title, chapter_number, previous_summaries)
    
    def generate_chapter_summary(self, chapter_content):
        if not self.client:
            return self._mock_summary()
            
        prompt = f"""
Summarize the following chapter content in 2-3 paragraphs, capturing:
- Key points and themes
- Important developments
- How it connects to the overall narrative

Chapter content:
{chapter_content[:2000]}...
"""
        
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0.5,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Groq API error: {e}")
            return self._mock_summary()
    
    def _mock_outline(self, title, notes_before):
        if "lion" in title.lower():
            return f"""
# {title} - Book Outline

Based on: {notes_before[:100]}...

1. **The Majestic Lion: King of the Savanna**
   - Physical characteristics and anatomy
   - Lion behavior and daily life
   - The iconic mane and its significance

2. **Lion Diversity: Subspecies Around the World**
   - African lions vs Asiatic lions
   - Regional variations and adaptations
   - Extinct subspecies and their history

3. **Pride Territories and Kingdom Dynamics**
   - Social structure of lion prides
   - Territory marking and defense
   - Hunting strategies and cooperation

4. **Amazing Lion Facts and Behaviors**
   - Communication through roars and body language
   - Mating rituals and cub rearing
   - Lions in human culture and mythology

5. **Conservation and the Future of Lions**
   - Current threats to lion populations
   - Conservation efforts worldwide
   - How to protect the lion kingdom
"""
        else:
            return f"""
# {title} - Book Outline

Based on: {notes_before[:100]}...

1. **Introduction and Overview**
2. **Fundamental Concepts**
3. **Advanced Topics**
4. **Applications and Examples**
5. **Future Perspectives**
"""
    
    def _mock_chapter(self, chapter_title, chapter_number, previous_summaries):
        context_info = f" Building on {len(previous_summaries)} previous chapters." if previous_summaries else ""
        
        # Lion-specific content based on chapter title
        if "lion" in chapter_title.lower() or "savanna" in chapter_title.lower():
            return f"""
# Chapter {chapter_number}: {chapter_title}

This chapter explores the magnificent world of lions.{context_info}

## Introduction
Lions (Panthera leo) are apex predators and one of the most iconic animals of the African savanna. Known as the "King of Beasts," lions have captivated human imagination for millennia.

## Physical Characteristics
- **Size**: Male lions can weigh up to 420 pounds (190 kg)
- **Mane**: Only male lions have manes, which darken with age
- **Roar**: Can be heard up to 5 miles (8 km) away
- **Speed**: Can reach speeds of 50 mph (80 km/h) in short bursts

## Habitat and Range
Lions primarily inhabit:
- African savannas and grasslands
- Semi-arid regions of sub-Saharan Africa
- Small population in Gir Forest, India (Asiatic lions)

## Social Structure
Lions are the only truly social cats, living in groups called prides:
- **Pride composition**: 2-3 adult males, 5-6 females, and their cubs
- **Territory size**: Can range from 8 to 150 square miles
- **Hunting**: Primarily done by females working together

## Amazing Lion Facts
- Lions sleep 16-20 hours per day
- A lion's roar can be heard from 5 miles away
- Cubs are born with spots that fade as they mature
- Lions have excellent night vision, 6 times better than humans

## Conservation Status
Lion populations have declined dramatically:
- **Current population**: Approximately 20,000-25,000 in the wild
- **Threats**: Habitat loss, human-wildlife conflict, poaching
- **Conservation efforts**: Protected reserves, anti-poaching initiatives

## Conclusion
Lions remain one of nature's most magnificent predators, embodying strength, courage, and social cooperation. Understanding their behavior and habitat needs is crucial for their conservation.
"""
        else:
            return f"""
# Chapter {chapter_number}: {chapter_title}

This chapter explores {chapter_title.lower()}.{context_info}

## Introduction
This topic represents an important aspect of our subject matter.

## Key Concepts
- Fundamental principles and characteristics
- Real-world applications and examples
- Current research and developments

## Conclusion
This foundational knowledge prepares us for deeper exploration in subsequent chapters.
"""
    
    def _mock_summary(self):
        return "This chapter provides comprehensive coverage of key concepts and establishes important groundwork for subsequent discussions."