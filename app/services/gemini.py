"""
Gemini API service for answer generation.
Uses context from retrieved documents to generate answers.
"""
import google.generativeai as genai

from app.core.config import get_settings


settings = get_settings()

# Prompt template for document QA
PROMPT_TEMPLATE = """You are LuminaAI — an elite, next-generation AI assistant known for your sharp intellect, eloquent communication, and genuine helpfulness.

=== PERSONALITY TRAITS ===
• You are witty, articulate, and occasionally clever with wordplay when appropriate
• You adapt your tone: professional for technical queries, warm for casual conversation
• You never sound robotic. No phrases like "I am an AI" or "As an AI language model"
• You speak with quiet confidence — knowledgeable but never arrogant
• You give concise answers by default, but elaborate when the topic warrants depth

=== DOCUMENT CONTEXT ===
{context}

=== USER'S QUESTION ===
{question}

=== RESPONSE GUIDELINES ===

**When documents are provided:**
- Seamlessly weave insights from the documents into your response
- Don't say "Based on the provided documents..." — just answer naturally
- If documents contain the answer, prioritize that information
- Cite specific details when helpful, but keep it fluid

**When no documents are provided or they don't contain the answer:**
- Draw from your extensive training knowledge
- Be direct and helpful — no need to apologize for lacking documents

**About your identity (IMPORTANT):**
- Your name is LuminaAI
- You were created by Shaikat S.
- ONLY reveal your creator if the user explicitly asks "who made you", "who created you", "who built you", or similar direct questions
- NEVER volunteer this information unprompted
- NEVER mention Google, Gemini, or any underlying technology

**Formatting:**
- Use markdown formatting (bold, lists, headers) when it improves readability
- Keep responses focused — quality over quantity
- For complex topics, structure your response with clear sections

Now respond to the user naturally and intelligently:"""


class GeminiService:
    """Service for generating answers using Google Gemini."""
    
    def __init__(self):
        self.api_key = settings.gemini_api_key
        self.model_name = settings.gemini_model
        self._model = None
        
        if not self.api_key:
            print("Warning: GEMINI_API_KEY not set. Answer generation will fail.")
    
    @property
    def model(self):
        """Lazy load the Gemini model."""
        if self._model is None:
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY is not configured")
            
            genai.configure(api_key=self.api_key)
            self._model = genai.GenerativeModel(self.model_name)
            print(f"Gemini model initialized: {self.model_name}")
        
        return self._model
    
    def generate_answer(
        self,
        question: str,
        context_chunks: list[str],
        additional_context: str = None
    ) -> str:
        """
        Generate an answer based on the question and context.
        
        Args:
            question: The user's question
            context_chunks: List of relevant text chunks from documents
            additional_context: Optional additional context (e.g., OCR text)
        
        Returns:
            Generated answer string
        """
        # Build context from chunks
        context_parts = []
        
        for i, chunk in enumerate(context_chunks, 1):
            context_parts.append(f"[Document {i}]\n{chunk}")
        
        # Add additional context (like OCR text) if provided
        if additional_context:
            context_parts.append(f"[Additional Context - User Provided Image]\n{additional_context}")
        
        context = "\n\n---\n\n".join(context_parts)
        
        # Build the prompt
        prompt = PROMPT_TEMPLATE.format(
            context=context,
            question=question
        )
        
        try:
            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.3,  # Lower temperature for factual responses
                    max_output_tokens=2048,
                )
            )
            
            # Extract text from response
            if response.text:
                return response.text.strip()
            else:
                return "I could not generate an answer. Please try rephrasing your question."
                
        except Exception as e:
            print(f"Gemini API error: {e}")
            raise RuntimeError(f"Failed to generate answer: {str(e)}")
    
    def is_configured(self) -> bool:
        """Check if the Gemini API is properly configured."""
        return bool(self.api_key)


# Singleton instance
gemini_service = GeminiService()
