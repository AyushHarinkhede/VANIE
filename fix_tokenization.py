# Simple fix for tokenization - replace the return statement
import sys
import os

# Read the file
with open('VANIE.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the simple return with enhanced logic
old_code = """        return cleaned_words"""
new_code = """        # Also add multi-word phrases for better matching
        phrases = []
        for i in range(len(words)):
            # Create multi-word phrases (2-3 words)
            if i < len(words) - 1:
                phrase2 = words[i] + " " + words[i+1]
                phrase2 = re.sub(r'[^\\w\\s]', '', phrase2)
                if phrase2 and phrase2 not in self.stop_words:
                    phrases.append(phrase2)
            
            if i < len(words) - 2:
                phrase3 = words[i] + " " + words[i+1] + " " + words[i+2]
                phrase3 = re.sub(r'[^\\w\\s]', '', phrase3)
                if phrase3 and phrase3 not in self.stop_words:
                    phrases.append(phrase3)
        
        # Combine single words and phrases
        return cleaned_words + phrases"""

# Replace the code
content = content.replace(old_code, new_code)

# Write back to file
with open('VANIE.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Tokenization function updated successfully!")
