import re

def preprocess_text(text):
    """Enhanced preprocessing for mental health text analysis."""
    
    # Initial cleanup - remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Check if the text appears to be in a chat format
    chat_patterns = [
        r'^(User|Patient|Me):', 
        r'\n(User|Patient|Me):',
        r'^\[\d{2}:\d{2}\]'  # Common timestamp pattern
    ]
    
    is_chat_format = any(re.search(pattern, text) for pattern in chat_patterns)
    
    if is_chat_format:
        # Split into segments based on speaker indicators
        segments = re.split(r'\n(?=(?:User|Patient|Me|Therapist|Doctor):)', text)
        
        # Process each segment to remove speaker labels but preserve content
        processed_segments = []
        current_speaker = None
        
        for segment in segments:
            # Extract speaker and content
            speaker_match = re.match(r'^(User|Patient|Me|Therapist|Doctor):\s*(.*)', segment, re.DOTALL)
            
            if speaker_match:
                speaker, content = speaker_match.groups()
                current_speaker = speaker
                processed_segments.append(content.strip())
            else:
                # No speaker label, but continue with previous speaker
                processed_segments.append(segment.strip())
        
        # Join all segments with proper punctuation and spacing
        processed_text = ""
        for i, segment in enumerate(processed_segments):
            # Ensure proper punctuation at the end of each segment
            if not segment.endswith(('.', '?', '!')):
                segment += '.'
            
            # Add the segment to the processed text
            if i == 0:
                processed_text = segment
            else:
                processed_text += " " + segment
    else:
        # Not a chat format, just clean up the text
        processed_text = text
        
        # Fix common punctuation issues
        processed_text = re.sub(r'\.{2,}', '.', processed_text)  # Replace multiple periods
        processed_text = re.sub(r'\s+([.,;:!?])', r'\1', processed_text)  # Fix spacing before punctuation
    
    # Normalize emotional indicators often seen in chats
    emoji_map = {
        r':[\(\[]': " feeling sad ",
        r':[\)\]]': " feeling happy ",
        r':\|': " feeling neutral ",
        r':\S': " feeling emotional "
    }
    
    for pattern, replacement in emoji_map.items():
        processed_text = re.sub(pattern, replacement, processed_text)
    
    return processed_text