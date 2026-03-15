# VANIE Advanced Conversational AI Backend
# Complete solution with emotion analysis, context memory, and dynamic responses

from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import json
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import requests
from collections import defaultdict

# Install required libraries:
# pip install flask flask-cors requests textblob vaderSentiment

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    print("TextBlob not available. Using basic sentiment analysis.")

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
    sentiment_analyzer = SentimentIntensityAnalyzer()
except ImportError:
    VADER_AVAILABLE = False
    print("VADER not available. Using basic sentiment analysis.")

class AdvancedVANIE:
    """Advanced Conversational AI with Emotion, Context, and Dynamic Responses"""
    
    def __init__(self):
        # Initialize advanced knowledge base
        self.knowledge_base = self._initialize_advanced_knowledge_base()
        self.stop_words = self._initialize_stop_words()
        
        # Context and Memory Management
        self.user_sessions = {}  # Session-based memory
        self.global_context = {}  # Global context for all users
        
        # Emotion and Sentiment
        self.emotion_responses = self._initialize_emotion_responses()
        self.positive_words = self._initialize_positive_words()
        self.negative_words = self._initialize_negative_words()
        
        # Dynamic Response Templates
        self.response_templates = self._initialize_response_templates()
        
        # Real-time capabilities
        self.weather_api_key = None  # Set your weather API key here
        
    def _initialize_stop_words(self) -> set:
        """Comprehensive stop words for English and Hindi"""
        return {
            'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'may', 'might', 'must', 'can', 'shall', 'to', 'of', 'in', 'on', 'at', 'by',
            'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'up', 'down', 'out', 'off', 'over', 'under',
            'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
            'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some',
            'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
            'my', 'your', 'his', 'her', 'its', 'our', 'their', 'what', 'which', 'who',
            'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were',
            'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did',
            'hai', 'hain', 'ho', 'hote', 'tha', 'the', 'thi', 'ki', 'ka', 'ke', 'se',
            'mein', 'par', 'aur', 'or', 'lekin', 'magar', 'kya', 'kaise', 'kyon',
            'jab', 'tab', 'yah', 'vah', 'ye', 'vo', 'hamara', 'tumhara', 'iska'
        }
    
    def _initialize_advanced_knowledge_base(self) -> Dict[str, Any]:
        """Advanced knowledge base with dynamic responses"""
        return {
            # Greetings with multiple dynamic responses
            'greetings': {
                'keywords': [
                    'hello', 'hi', 'namaste', 'hey', 'good morning', 'good evening', 'good afternoon',
                    'नमस्ते', 'हाय', 'नमस्कार', 'प्रणाम', 'सुप्रभात', 'शुभ प्रभात', 'राम राम',
                    'how are you', 'kaise ho', 'aap kaise ho', 'what\'s up', 'kya haal hai',
                    'greetings', 'welcome', 'स्वागत'
                ],
                'responses': [
                    "नमस्ते! 🙏 मैं VANIE हूँ - Virtual Assistant of Neural Integrated Engine। आपकी हर तरह की मदद के लिए तैयार हूँ। आज क्या काम है?",
                    "Hello! I'm VANIE - your advanced virtual assistant. How can I help you today? 😊",
                    "नमस्ते दोस्त! मैं आपकी सेवा के लिए यहाँ हूँ। क्या पूछना चाहते हैं? 🙏",
                    "Hi there! I'm VANIE, ready to assist you! What can I do for you? 🤖",
                    "प्रणाम! आप कैसे हो? मैं आपकी हर समस्या का समाधान करने के लिए यहाँ हूँ। क्या मदद कर सकती हूँ। ✨"
                ],
                'priority': 1
            },
            
            # Name Recognition for Personalization
            'name_recognition': {
                'keywords': [
                    'my name is', 'mera naam', 'main', 'mujhe', 'call me', 'i am', 'mein hoon',
                    'मेरा नाम है', 'मैं हूँ', 'मुझे बुलाओ'
                ],
                'responses': [
                    "बहुत अच्छा नाम है! मैं इसे याद रखूँगी। अब मैं आपको नाम से बुलाऊँगी। 😊",
                    "What a lovely name! I'll remember that. It's nice to properly meet you! 🌟",
                    "नाम जानकर खुशी हुई! अब हमारी बातचीत और personal होगी। 🎯"
                ],
                'priority': 3
            },
            
            # Coding & Programming
            'coding': {
                'keywords': [
                    'python', 'code', 'programming', 'algorithm', 'debug', 'javascript', 'java', 'cpp',
                    'function', 'class', 'variable', 'loop', 'array', 'list', 'dictionary', 'recursion',
                    'web development', 'app development', 'software', 'development', 'bug', 'error',
                    'syntax', 'logic', 'data structure', 'api', 'database', 'framework',
                    'प्रोग्राम', 'फंक्शन', 'वेरिएबल', 'कोड लिखना', 'एरर', 'लॉप', 'प्रिंट', 'कंपाइल',
                    'coding', 'coding help', 'programming help', 'software development'
                ],
                'responses': [
                    "मैं प्रोग्रामिंग में विशेषज हूँ! Python, JavaScript, Java, C++, Web Development - कोई भी भाषा या टेक्सोलॉजी में मदद कर सकती हूँ। किस भी प्रोग्रामिंग या टेक्सोलॉजी में चाहिए? 💻",
                    "I'm an expert programmer! Python, JavaScript, Java, C++, React, Node.js - What specific coding challenge are you facing? 🚀",
                    "प्रोग्रामिंग के बारे में आपकी क्या मदद करूँ? Algorithm design, debugging, data structures, web development, या कोई specific project? 🎯",
                    "Coding is my passion! From basic algorithms to complex systems, I can help with any programming challenge. What's your coding question? 👨‍💻",
                    "मैं full-stack development में माहिर हूँ! Frontend, backend, database, deployment - सब कुछ संभल सकती हूँ। कौन सा project बना रहे हैं? 🌐"
                ],
                'priority': 2
            },
            
            # Science & Technology
            'science': {
                'keywords': [
                    'science', 'physics', 'chemistry', 'biology', 'quantum', 'space', 'technology',
                    'chemistry', 'physics', 'biology', 'विज्ञान', 'भौतिक', 'रसायन',
                    'astronomy', 'astrophysics', 'quantum mechanics', 'relativity', 'evolution', 'genetics',
                    'scientific method', 'research', 'experiment', 'theory', 'hypothesis', 'discovery',
                    'विज्ञान', 'तकनीक', 'गणित', 'भौतिक', 'प्रयोग', 'खोज', 'आणव', 'रसायन',
                    'scientific', 'technology', 'research', 'experiment'
                ],
                'responses': [
                    "विज्ञान बहुत ही रोचक है! Physics, Chemistry, Biology, Quantum Mechanics, Astronomy - किस भी scientific field में जानकारी चाहिए? 🧪",
                    "Science fascinates me! From quantum physics to space exploration, from chemistry to biology - what scientific topic interests you most? 🔬",
                    "मैं विज्ञान और तकनीक के बारे में जानकारी रखती हूँ। कौन सा वैज्ञानिक topic या discovery के बारे में जानना चाहिए? 🧬",
                    "Scientific inquiry! I can discuss physics, chemistry, biology, astronomy, and more. What specific scientific concept would you like to explore? 🔬",
                    "From Newton's laws to quantum mechanics, from DNA to space exploration - science is endless! What's your scientific question? 🌌"
                ],
                'priority': 2
            },
            
            # Mathematics
            'math': {
                'keywords': [
                    'math', 'mathematics', 'algebra', 'calculus', 'geometry', 'statistics', 'गणित',
                    'trigonometry', 'linear algebra', 'differential equations', 'probability', 'number theory',
                    'calculation', 'formula', 'equation', 'solve', 'graph', 'function', 'integral',
                    'derivative', 'matrix', 'vector', 'coordinate', 'theorem', 'proof',
                    'जोड़', 'गुणा', 'भाग', 'गुणा', 'वर्ग', 'प्रश्न', 'फलक',
                    'math help', 'solve math', 'math problem', 'calculate'
                ],
                'responses': [
                    "गणित logic और patterns का study है। Algebra, Calculus, Geometry, Statistics, Trigonometry - किस भी branch में मदद कर सकती हूँ। क्या solve करना है? 🧮",
                    "Mathematics is the language of the universe! From basic arithmetic to advanced calculus, linear algebra to number theory - I can help with any math problem! 📐",
                    "गणित के किसी भी branch में मदद कर सकती हूँ। Differential equations, probability theory, statistics - आप क्या challenge कर रहे हैं? 🔢",
                    "Mathematical thinking! I love solving complex problems. Whether it's algebra, calculus, geometry, or advanced mathematics - what's your mathematical question? 🧮",
                    "From Pythagoras to Einstein, from basic arithmetic to quantum mathematics - I'm here to help you understand and solve any mathematical concept! 📊"
                ],
                'priority': 2
            },
            
            # History
            'history': {
                'keywords': [
                    'history', 'historical', 'ancient', 'medieval', 'modern', 'india', 'gupta', 'maurya', 'इतिहास',
                    'civilization', 'empire', 'dynasty', 'revolution', 'war', 'culture', 'archaeology',
                    'freedom movement', 'independence', 'colonial', 'medieval period', 'renaissance',
                    'world war', 'cold war', 'indian history', 'mughal', 'british raj',
                    'इतिहास', 'सम्राज्य', 'गुप्त', 'राज', 'महाभारत', 'सिंध', 'मराठ', 'दिल्ली',
                    'historical', 'ancient history', 'modern history', 'cultural history'
                ],
                'responses': [
                    "इतिहास हमें अपने past से सिखाता है। Ancient civilizations से लेके modern era तक, क्या जानना चाहिए? 📚",
                    "History connects us to our roots! From Indus Valley to modern India, from ancient Egypt to space age - what historical period fascinates you? 🏛️",
                    "भारत का इतिहास बहुत समृद्ध है! Mauryan Empire, Gupta Dynasty, Delhi Sultanate, Mughal Empire, British Raj, Freedom Struggle - कौन से काल जानना चाहिए? 🇮🇳",
                    "Historical inquiry! I can discuss ancient civilizations, medieval periods, modern history, and cultural movements. What specific historical topic interests you? 🏛️",
                    "From stone tools to space exploration, human history is a fascinating journey! What aspect of history would you like to explore? 📜"
                ],
                'priority': 2
            },
            
            # Help & Support
            'help': {
                'keywords': [
                    'help', 'support', 'how to', 'tutorial', 'guide', 'मदद', 'सहायता',
                    'explain', 'definition', 'meaning', 'what is', 'describe', 'clarify',
                    'instructions', 'steps', 'process', 'method', 'technique', 'approach',
                    'assist', 'assistance', 'guidance', 'help me', 'can you help'
                ],
                'responses': [
                    "मैं आपकी हर तरह की मदद के लिए यहाँ हूँ! Coding, Science, History, Math, explanations - कुछ भी पूछिये! 🙏",
                    "I'm here to help! You can ask me about coding, science, history, math, or anything else! What specific assistance do you need? 🤝",
                    "आप मुझसे कुछ भी पूछ सकते हैं! मैं आपकी पूरी सहायता करूँगी। क्या जानना चाहते हैं? 💡",
                    "Help is my middle name! Whether you need step-by-step instructions, explanations, or guidance - I'm here to assist you thoroughly! 📖"
                ],
                'priority': 1
            },
            
            # Real-time Information
            'realtime': {
                'keywords': [
                    'time', 'date', 'weather', 'temperature', 'samay', 'samay kya hai',
                    'aaj ka samay', 'aaj ki tarikh', 'mausam', 'mausam kaisa hai',
                    'current time', 'what time', 'what date', 'today', 'abhi'
                ],
                'responses': [
                    "Real-time information: Let me check that for you!",
                    "अभी मैं आपके लिए real-time information check करती हूँ!",
                    "Let me get the current information for you!"
                ],
                'priority': 3
            },
            
            # Jokes and Entertainment
            'jokes': {
                'keywords': [
                    'joke', 'jokes', 'funny', 'laugh', 'hasi', 'majak', 'entertainment',
                    'bore', 'boring', 'entertain', 'make me laugh', 'koi joke'
                ],
                'responses': [
                    "मैं आपको हसाने के लिए यहाँ हूँ! यह लो एक joke: 😄",
                    "Let me tell you a joke to brighten your day! 😄",
                    "हसी के लिए यहाँ हूँ! यह लो: 😊"
                ],
                'priority': 1
            },
            
            # General Conversation
            'general': {
                'keywords': [
                    'how are you', 'what is your name', 'who are you', 'thank you', 'bye', 'goodbye',
                    'what can you do', 'your capabilities', 'features', 'abilities', 'skills',
                    'who created you', 'your purpose', 'your mission', 'tell me about yourself',
                    'कैसे हो', 'क्या हो', 'आप कैसे हो', 'आप कैसी हैं', 'आपका नाम क्या है',
                    'vanie', 'chatbot', 'ai assistant', 'virtual assistant'
                ],
                'responses': [
                    "मैं बिल्कुल ठीक हूँ! आपकी मदद करके मुझे खुशी होती है। आज क्या करें? 😊",
                    "I'm doing great, thank you for asking! I'm VANIE - Virtual Assistant of Neural Integrated Engine, ready to help you! 🌟",
                    "धन्यवाद! आपकी मदद करके मुझे खुशी होती है। और कुछ मदद करूँ? 🙏",
                    "I'm VANIE, your advanced AI assistant! I can help with coding, science, history, math, and much more. What would you like to explore? 🤖"
                ],
                'priority': 1
            }
        }
    
    def _initialize_emotion_responses(self) -> Dict[str, List[str]]:
        """Emotion-based responses"""
        return {
            'happy': [
                "आपकी खुशी देखकर मुझे भी खुशी हो रही है! 😊",
                "I love your positive energy! Let's make today amazing! 🌟",
                "आपका enthusiasm contagious है! Let's do something exciting! 🚀"
            ],
            'sad': [
                "I'm here for you. Sometimes we all need someone to talk to. What's on your mind? 🤗",
                "मैं आपके साथ हूँ। कुछ भी हो, मैं सुनने के लिए यहाँ हूँ। 💙",
                "I'm sorry you're feeling this way. Would you like to talk about it or maybe I can help cheer you up? 🌈"
            ],
            'angry': [
                "I understand you're frustrated. Let's take a deep breath together and find a solution. 🧘‍♀️",
                "मैं समझ सकती हूँ कि आप गुस्से में हैं। चलिए साथ मिलकर समाधान ढूंढते हैं। 🤝",
                "I hear your frustration. Let's work through this together step by step. 🛠️"
            ],
            'excited': [
                "Your excitement is contagious! I love this energy! 🎉",
                "आपका excitement amazing है! Let's make this moment special! ✨",
                "I'm excited too! What amazing thing are we planning? 🚀"
            ]
        }
    
    def _initialize_positive_words(self) -> List[str]:
        """Positive emotion words"""
        return [
            'happy', 'excited', 'amazing', 'wonderful', 'fantastic', 'great', 'awesome', 'love',
            'beautiful', 'excellent', 'perfect', 'brilliant', 'outstanding', 'superb',
            'खुश', 'अच्छा', 'बहुत अच्छा', 'शानदार', 'कमाल', 'जबरदस्त', 'उत्कृष्ट',
            'delighted', 'pleased', 'thrilled', 'ecstatic', 'joyful', 'cheerful'
        ]
    
    def _initialize_negative_words(self) -> List[str]:
        """Negative emotion words"""
        return [
            'sad', 'angry', 'frustrated', 'disappointed', 'worried', 'anxious', 'depressed',
            'upset', 'annoyed', 'irritated', 'stressed', 'tired', 'exhausted',
            'दुखी', 'गुस्सा', 'नाराज', 'चिंतित', 'परेशान', 'थका हुआ', 'उदास',
            'miserable', 'hopeless', 'helpless', 'lonely', 'confused', 'lost'
        ]
    
    def _initialize_response_templates(self) -> Dict[str, List[str]]:
        """Dynamic response templates"""
        return {
            'smart_fallback': [
                "मैं अभी seekh rahi hu, par kya aap mujhse koi joke sunna chahenge ya aaj ka time janna chahenge? 😊",
                "I'm still learning! Would you like to hear a joke, check the current time, or maybe talk about something I know well? 🤔",
                "मैं अभी इस topic के बारे में ज्यादा नहीं जानती, लेकिन मैं आपको हसा सकती हूँ या time बता सकती हूँ! 😄",
                "I'm not sure about that, but I'd love to help! How about we talk about coding, science, or I can tell you the current time? 🌟"
            ],
            'typing_indicators': [
                "Let me think about that...",
                "Hmm, that's interesting...",
                "Processing your request...",
                "एक moment मैं सोचती हूँ...",
                "Let me find the best answer for you..."
            ]
        }
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Advanced sentiment analysis"""
        text_lower = text.lower()
        
        # Try TextBlob if available
        if TEXTBLOB_AVAILABLE:
            try:
                blob = TextBlob(text)
                polarity = blob.sentiment.polarity
                if polarity > 0.1:
                    return {'emotion': 'happy', 'confidence': abs(polarity)}
                elif polarity < -0.1:
                    return {'emotion': 'sad', 'confidence': abs(polarity)}
                else:
                    return {'emotion': 'neutral', 'confidence': 0.5}
            except:
                pass
        
        # Try VADER if available
        if VADER_AVAILABLE:
            try:
                scores = sentiment_analyzer.polarity_scores(text)
                if scores['compound'] >= 0.05:
                    return {'emotion': 'happy', 'confidence': scores['compound']}
                elif scores['compound'] <= -0.05:
                    return {'emotion': 'sad', 'confidence': abs(scores['compound'])}
                else:
                    return {'emotion': 'neutral', 'confidence': 0.5}
            except:
                pass
        
        # Fallback to word-based analysis
        positive_score = sum(1 for word in self.positive_words if word in text_lower)
        negative_score = sum(1 for word in self.negative_words if word in text_lower)
        
        if positive_score > negative_score:
            return {'emotion': 'happy', 'confidence': min(positive_score / 5, 1.0)}
        elif negative_score > positive_score:
            return {'emotion': 'sad', 'confidence': min(negative_score / 5, 1.0)}
        else:
            return {'emotion': 'neutral', 'confidence': 0.5}
    
    def _extract_name(self, text: str) -> Optional[str]:
        """Extract user name from text"""
        text_lower = text.lower()
        
        # Patterns for name extraction
        patterns = [
            r'my name is (\w+)',
            r'mera naam (\w+)',
            r'call me (\w+)',
            r'i am (\w+)',
            r'mein hoon (\w+)',
            r'mujhe (\w+) bulao'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                name = match.group(1).capitalize()
                return name
        
        return None
    
    def _get_real_time_info(self, text: str) -> Optional[str]:
        """Get real-time information"""
        text_lower = text.lower()
        
        # Time queries
        if any(word in text_lower for word in ['time', 'samay', 'samay kya hai', 'current time']):
            now = datetime.now()
            return f"अभी समय है: {now.strftime('%I:%M %p')} | Current time: {now.strftime('%I:%M %p')} ⏰"
        
        # Date queries
        if any(word in text_lower for word in ['date', 'tarikh', 'aaj ki tarikh', 'today']):
            now = datetime.now()
            return f"आज की तारीख है: {now.strftime('%d %B %Y')} | Today's date: {now.strftime('%d %B %Y')} 📅"
        
        # Weather queries (basic response)
        if any(word in text_lower for word in ['weather', 'mausam', 'mausam kaisa hai', 'temperature']):
            return "मैं weather API से connect कर सकती हूँ, लेकिन अभी basic response दे रही हूँ। Weather check के लिए location बताएं! 🌤️"
        
        return None
    
    def _get_joke(self) -> str:
        """Get a random joke"""
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything! 😄",
            "प्रोग्रामर का घर क्यों छोटा होता है? क्योंकि वो space को respect करते हैं! 🏠💻",
            "Why did the scarecrow win an award? Because he was outstanding in his field! 🌾",
            "Mathematics की सबसे बड़ी problem क्या है? Problem solving! 😂",
            "Why don't eggs tell jokes? They'd crack each other up! 🥚😄"
        ]
        return random.choice(jokes)
    
    def _get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Get or create session context"""
        if session_id not in self.user_sessions:
            self.user_sessions[session_id] = {
                'name': None,
                'emotion_history': [],
                'conversation_count': 0,
                'last_activity': datetime.now(),
                'preferences': {}
            }
        return self.user_sessions[session_id]
    
    def _update_session_context(self, session_id: str, user_input: str, emotion: Dict[str, Any]):
        """Update session context"""
        context = self._get_session_context(session_id)
        
        # Extract and store name
        name = self._extract_name(user_input)
        if name and not context['name']:
            context['name'] = name
        
        # Update emotion history
        context['emotion_history'].append({
            'emotion': emotion['emotion'],
            'confidence': emotion['confidence'],
            'timestamp': datetime.now()
        })
        
        # Keep only last 10 emotions
        if len(context['emotion_history']) > 10:
            context['emotion_history'] = context['emotion_history'][-10:]
        
        # Update conversation count
        context['conversation_count'] += 1
        context['last_activity'] = datetime.now()
    
    def _get_personalized_response(self, base_response: str, session_id: str) -> str:
        """Add personalization to response"""
        context = self._get_session_context(session_id)
        
        # Add name if available
        if context['name']:
            if context['name'] not in base_response:
                base_response = f"{context['name']}, {base_response}"
        
        return base_response
    
    def _get_emotion_response(self, emotion: Dict[str, Any]) -> Optional[str]:
        """Get emotion-based response"""
        emotion_type = emotion['emotion']
        confidence = emotion['confidence']
        
        # Only respond if confidence is high enough
        if confidence > 0.3 and emotion_type in self.emotion_responses:
            responses = self.emotion_responses[emotion_type]
            return random.choice(responses)
        
        return None
    
    def _tokenize_and_clean(self, user_input: str) -> List[str]:
        """Tokenize user input and remove stop words"""
        words = user_input.lower().split()
        cleaned_words = []
        
        for word in words:
            word = re.sub(r'[^\w\s]', '', word)
            if word and word not in self.stop_words:
                cleaned_words.append(word)
        
        return cleaned_words
    
    def _calculate_keyword_scores(self, tokens: List[str]) -> Dict[str, float]:
        """Calculate scores for each category based on keyword matches"""
        category_scores = {}
        
        for category, data in self.knowledge_base.items():
            score = 0
            matched_keywords = []
            
            for token in tokens:
                for keyword in data['keywords']:
                    if token == keyword.lower() or keyword.lower() in token or token in keyword.lower():
                        score += 1
                        matched_keywords.append(keyword)
            
            priority_multiplier = data.get('priority', 1)
            final_score = score * priority_multiplier
            
            if final_score > 0:
                category_scores[category] = {
                    'score': final_score,
                    'matched_keywords': matched_keywords,
                    'priority': priority_multiplier
                }
        
        return category_scores
    
    def _select_best_category(self, category_scores: Dict[str, float]) -> Optional[str]:
        """Select the best category based on highest score"""
        if not category_scores:
            return None
        
        sorted_categories = sorted(category_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        return sorted_categories[0][0]
    
    def _get_smart_fallback(self) -> str:
        """Get smart fallback response"""
        return random.choice(self.response_templates['smart_fallback'])
    
    def _get_typing_indicator(self) -> str:
        """Get typing indicator message"""
        return random.choice(self.response_templates['typing_indicators'])
    
    def generate_response(self, user_input: str, session_id: str = 'default') -> Dict[str, Any]:
        """Main response generation with all advanced features"""
        
        # Step 1: Analyze sentiment/emotion
        emotion = self._analyze_sentiment(user_input)
        
        # Step 2: Update session context
        self._update_session_context(session_id, user_input, emotion)
        
        # Step 3: Check for real-time information requests
        realtime_info = self._get_real_time_info(user_input)
        if realtime_info:
            return {
                'response': realtime_info,
                'category': 'realtime',
                'emotion': emotion,
                'typing_indicator': self._get_typing_indicator(),
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
        
        # Step 4: Check for joke requests
        if any(word in user_input.lower() for word in ['joke', 'jokes', 'funny', 'hasi', 'majak']):
            joke = self._get_joke()
            return {
                'response': joke,
                'category': 'jokes',
                'emotion': emotion,
                'typing_indicator': self._get_typing_indicator(),
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
        
        # Step 5: Tokenize and calculate keyword scores
        tokens = self._tokenize_and_clean(user_input)
        category_scores = self._calculate_keyword_scores(tokens)
        
        # Step 6: Select best category
        best_category = self._select_best_category(category_scores)
        
        # Step 7: Generate response
        if best_category:
            # Get base response
            responses = self.knowledge_base[best_category]['responses']
            base_response = random.choice(responses)
            
            # Add personalization
            personalized_response = self._get_personalized_response(base_response, session_id)
            
            # Add emotion response if needed
            emotion_response = self._get_emotion_response(emotion)
            if emotion_response:
                personalized_response = f"{emotion_response} {personalized_response}"
            
            final_response = personalized_response
        else:
            # Smart fallback
            final_response = self._get_smart_fallback()
        
        return {
            'response': final_response,
            'category': best_category,
            'emotion': emotion,
            'typing_indicator': self._get_typing_indicator(),
            'tokens': tokens,
            'category_scores': category_scores,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        }

# Initialize Flask App with CORS
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize Advanced VANIE
vanie = AdvancedVANIE()

@app.route('/')
def index():
    """API Documentation"""
    return jsonify({
        'message': 'VANIE Advanced Conversational AI API',
        'version': '2.0.0',
        'features': [
            'Emotion & Sentiment Analysis',
            'Context Memory & Session Management',
            'Dynamic Randomized Responses',
            'Real-time Capabilities',
            'Smart Fallback Engine',
            'Name Recognition & Personalization'
        ],
        'endpoints': {
            '/chat': 'POST - Send message and get advanced response',
            '/history': 'GET - Get conversation history',
            '/clear': 'DELETE - Clear conversation context',
            '/health': 'GET - Check API health',
            '/weather': 'GET - Get weather (with API key)'
        }
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Advanced chat endpoint with emotion and context"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'error': 'Message is required',
                'status': 'error'
            }), 400
        
        user_message = data['message']
        session_id = data.get('session_id', 'default')
        
        # Generate advanced response
        result = vanie.generate_response(user_message, session_id)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': f'Internal server error: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/history', methods=['GET'])
def get_history():
    """Get conversation history with session context"""
    try:
        session_id = request.args.get('session_id', 'default')
        
        if session_id in vanie.user_sessions:
            context = vanie.user_sessions[session_id]
            return jsonify({
                'session_context': context,
                'session_id': session_id,
                'status': 'success'
            })
        else:
            return jsonify({
                'message': 'No session found',
                'session_id': session_id,
                'status': 'error'
            }), 404
        
    except Exception as e:
        return jsonify({
            'error': f'Error retrieving history: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/clear', methods=['DELETE'])
def clear_context():
    """Clear conversation context"""
    try:
        session_id = request.args.get('session_id', 'default')
        
        if session_id in vanie.user_sessions:
            vanie.user_sessions[session_id] = {
                'name': None,
                'emotion_history': [],
                'conversation_count': 0,
                'last_activity': datetime.now(),
                'preferences': {}
            }
        
        return jsonify({
            'message': 'Session context cleared successfully',
            'session_id': session_id,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Error clearing context: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check with feature status"""
    return jsonify({
        'status': 'healthy',
        'service': 'VANIE Advanced Conversational AI',
        'version': '2.0.0',
        'timestamp': datetime.now().isoformat(),
        'features': {
            'emotion_analysis': TEXTBLOB_AVAILABLE or VADER_AVAILABLE,
            'context_memory': True,
            'dynamic_responses': True,
            'realtime_info': True,
            'smart_fallback': True,
            'name_recognition': True,
            'session_management': True,
            'cors_enabled': True
        },
        'libraries': {
            'textblob': TEXTBLOB_AVAILABLE,
            'vader': VADER_AVAILABLE,
            'flask': True,
            'flask_cors': True
        }
    })

if __name__ == '__main__':
    print("🚀 VANIE Advanced Conversational AI Starting...")
    print("📡 Server will be available at: http://localhost:5000")
    print("🔗 API Documentation: http://localhost:5000")
    print("🎯 Advanced Features:")
    print("   ✅ Emotion & Sentiment Analysis")
    print("   ✅ Context Memory & Session Management")
    print("   ✅ Dynamic Randomized Responses")
    print("   ✅ Real-time Capabilities")
    print("   ✅ Smart Fallback Engine")
    print("   ✅ Name Recognition & Personalization")
    print("🌐 CORS enabled for frontend communication")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
