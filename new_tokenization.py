def _tokenize_and_clean(self, user_input: str) -> List[str]:
        """Tokenize user input and remove stop words"""
        words = user_input.lower().split()
        cleaned_words = []
        
        # Also add multi-word phrases for better matching
        phrases = []
        for i in range(len(words)):
            word = words[i]
            # Remove punctuation and special characters
            word = re.sub(r'[^\w\s]', '', word)
            
            # Skip stop words and empty strings
            if word and word not in self.stop_words:
                cleaned_words.append(word)
            
            # Create multi-word phrases (2-3 words)
            if i < len(words) - 1:
                phrase2 = words[i] + " " + words[i+1]
                phrase2 = re.sub(r'[^\w\s]', '', phrase2)
                if phrase2 and phrase2 not in self.stop_words:
                    phrases.append(phrase2)
            
            if i < len(words) - 2:
                phrase3 = words[i] + " " + words[i+1] + " " + words[i+2]
                phrase3 = re.sub(r'[^\w\s]', '', phrase3)
                if phrase3 and phrase3 not in self.stop_words:
                    phrases.append(phrase3)
        
        # Combine single words and phrases
        return cleaned_words + phrases
