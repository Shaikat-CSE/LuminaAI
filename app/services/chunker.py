"""
Text chunking service for splitting documents into embedable chunks.
Uses tiktoken for accurate token counting.
"""
import re
from dataclasses import dataclass
from typing import Optional

import tiktoken

from app.core.config import get_settings


settings = get_settings()


@dataclass
class TextChunk:
    """Represents a chunk of text with metadata."""
    text: str
    chunk_id: int
    start_char: int
    end_char: int
    token_count: int


class TextChunker:
    """
    Split text into chunks suitable for embedding.
    Uses sentence-aware splitting to maintain context.
    """
    
    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None,
        encoding_name: str = "cl100k_base"
    ):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        self.encoder = tiktoken.get_encoding(encoding_name)
        
        # Sentence splitting patterns
        self.sentence_endings = re.compile(r'(?<=[.!?])\s+')
        self.paragraph_split = re.compile(r'\n\s*\n')
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoder.encode(text))
    
    def chunk_text(self, text: str) -> list[TextChunk]:
        """
        Split text into chunks with approximate token count.
        Tries to split on sentence boundaries when possible.
        """
        if not text or not text.strip():
            return []
        
        # Clean the text
        text = self._clean_text(text)
        
        # First, split by paragraphs
        paragraphs = self.paragraph_split.split(text)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        chunks = []
        current_chunk = ""
        current_tokens = 0
        chunk_id = 0
        start_char = 0
        
        for para in paragraphs:
            para_tokens = self.count_tokens(para)
            
            # If single paragraph is larger than chunk size, split by sentences
            if para_tokens > self.chunk_size:
                # Save current chunk if any
                if current_chunk:
                    chunks.append(TextChunk(
                        text=current_chunk.strip(),
                        chunk_id=chunk_id,
                        start_char=start_char,
                        end_char=start_char + len(current_chunk),
                        token_count=current_tokens
                    ))
                    chunk_id += 1
                    start_char += len(current_chunk)
                    current_chunk = ""
                    current_tokens = 0
                
                # Split paragraph by sentences
                sentence_chunks = self._split_paragraph(para)
                for sent_chunk in sentence_chunks:
                    chunks.append(TextChunk(
                        text=sent_chunk.strip(),
                        chunk_id=chunk_id,
                        start_char=start_char,
                        end_char=start_char + len(sent_chunk),
                        token_count=self.count_tokens(sent_chunk)
                    ))
                    chunk_id += 1
                    start_char += len(sent_chunk)
            
            # If adding paragraph exceeds chunk size, save current and start new
            elif current_tokens + para_tokens > self.chunk_size:
                if current_chunk:
                    chunks.append(TextChunk(
                        text=current_chunk.strip(),
                        chunk_id=chunk_id,
                        start_char=start_char,
                        end_char=start_char + len(current_chunk),
                        token_count=current_tokens
                    ))
                    chunk_id += 1
                    
                    # Apply overlap - take last portion of current chunk
                    overlap_text = self._get_overlap_text(current_chunk)
                    start_char += len(current_chunk) - len(overlap_text)
                    current_chunk = overlap_text + "\n\n" + para if overlap_text else para
                    current_tokens = self.count_tokens(current_chunk)
                else:
                    current_chunk = para
                    current_tokens = para_tokens
            else:
                # Add paragraph to current chunk
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
                current_tokens = self.count_tokens(current_chunk)
        
        # Don't forget the last chunk
        if current_chunk.strip():
            chunks.append(TextChunk(
                text=current_chunk.strip(),
                chunk_id=chunk_id,
                start_char=start_char,
                end_char=start_char + len(current_chunk),
                token_count=current_tokens
            ))
        
        return chunks
    
    def _split_paragraph(self, paragraph: str) -> list[str]:
        """Split a large paragraph into sentence-based chunks."""
        sentences = self.sentence_endings.split(paragraph)
        chunks = []
        current = ""
        current_tokens = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            sent_tokens = self.count_tokens(sentence)
            
            # If single sentence is too long, force split by character
            if sent_tokens > self.chunk_size:
                if current:
                    chunks.append(current)
                    current = ""
                    current_tokens = 0
                
                # Force split long sentence
                chunks.extend(self._force_split(sentence))
            
            elif current_tokens + sent_tokens > self.chunk_size:
                if current:
                    chunks.append(current)
                    # Apply overlap
                    overlap_text = self._get_overlap_text(current)
                    current = overlap_text + " " + sentence if overlap_text else sentence
                    current_tokens = self.count_tokens(current)
                else:
                    current = sentence
                    current_tokens = sent_tokens
            else:
                if current:
                    current += " " + sentence
                else:
                    current = sentence
                current_tokens = self.count_tokens(current)
        
        if current:
            chunks.append(current)
        
        return chunks
    
    def _force_split(self, text: str) -> list[str]:
        """Force split text that's too long for a single chunk."""
        chunks = []
        words = text.split()
        current = ""
        
        for word in words:
            test = current + " " + word if current else word
            if self.count_tokens(test) > self.chunk_size:
                if current:
                    chunks.append(current)
                current = word
            else:
                current = test
        
        if current:
            chunks.append(current)
        
        return chunks
    
    def _get_overlap_text(self, text: str) -> str:
        """Get the last portion of text for overlap."""
        if not text or self.chunk_overlap <= 0:
            return ""
        
        words = text.split()
        overlap_words = []
        token_count = 0
        
        for word in reversed(words):
            new_count = self.count_tokens(word)
            if token_count + new_count > self.chunk_overlap:
                break
            overlap_words.insert(0, word)
            token_count += new_count
        
        return " ".join(overlap_words)
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove excessive newlines but preserve paragraph breaks
        text = re.sub(r'\n{3,}', '\n\n', text)
        # Strip leading/trailing whitespace
        text = text.strip()
        return text


# Singleton instance
text_chunker = TextChunker()
