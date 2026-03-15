# VANIE Complete Backend - All-in-One Single File Solution
# Advanced AI with Multi-Keyword Scoring, Memory, Emotion Analysis, and NLP

# ========================================
# SECTION 1: IMPORTS & SETUP
# ========================================
from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import re
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import deque
import requests
import hashlib

# Try to import NLP libraries - fallback to basic if not available
try:
    import spacy
    SPACY_AVAILABLE = True
    # Load small English model for semantic understanding
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        print("⚠️ spaCy model not found. Run: python -m spacy download en_core_web_sm")
        SPACY_AVAILABLE = False
        nlp = None
except ImportError:
    SPACY_AVAILABLE = False
    nlp = None
    print("⚠️ spaCy not installed. Run: pip install spacy")

# Try to import sentence transformers for semantic similarity
try:
    from sentence_transformers import SentenceTransformer, util
    SENTENCE_TRANSFORMERS_AVAILABLE = True
    # Load a lightweight model for semantic understanding
    sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    sentence_model = None
    print("⚠️ Sentence Transformers not installed. Run: pip install sentence-transformers")

# ========================================
# SECTION 2: COMPLETE KNOWLEDGE BASE
# ========================================
class VANIEKnowledgeBase:
    """Complete knowledge base with intents, keywords, and responses"""
    
    @staticmethod
    def get_intents():
        return {
            # 1. Greetings & Small Talk Intent
            'greeting': {
                'keywords': [
                    'hi', 'hello', 'hey', 'hey there', 'good morning', 'good afternoon', 'good evening',
                    'good night', 'greetings', 'welcome', 'what\'s up', 'whats up', 'sup', 'yo',
                    'how are you', 'howdy', 'how do you do', 'nice to meet you', 'pleased to meet you',
                    'नमस्ते', 'नमस्कार', 'प्रणाम', 'राम राम', 'हाय', 'हेलो', 'हे',
                    'कैसे हो', 'कैसी हो', 'कैसी हैं', 'क्या हाल है', 'क्या हाल चाल',
                    'सुप्रभात', 'शुभ प्रभात', 'शुभ रात्रि', 'आप कैसे हो',
                    'kaise ho', 'kya haal hai', 'good morning', 'good evening', 'aur batao',
                    'whats up', 'sup', 'how are you', 'namaste', 'pranam'
                ],
                'responses': [
                    "नमस्ते! 🙏 मैं VANIE हूँ - Virtual Assistant of Neural Integrated Engine। आपकी हर तरह की मदद के लिए तैयार हूँ। आज क्या काम है?",
                    "Hello! I'm VANIE - your advanced virtual assistant. How can I help you today? 😊",
                    "नमस्ते दोस्त! मैं आपकी सेवा के लिए यहाँ हूँ। क्या पूछना चाहते हैं? 🙏",
                    "Hi there! I'm VANIE, ready to assist you! What can I do for you? 🤖",
                    "प्रणाम! आप कैसे हो? मैं आपकी हर समस्या का समाधान करने के लिए यहाँ हूँ। क्या मदद कर सकती हूँ। ✨",
                    "Hey! VANIE at your service! What can I help you with today? 🌟"
                ],
                'priority': 1
            },
            
            # 2. Identity & Creator Intent
            'identity': {
                'keywords': [
                    'who are you', 'what are you', 'what is your name', 'your name', 'tell me about yourself',
                    'introduce yourself', 'what is vanie', 'what does vanie stand for',
                    'who made you', 'who created you', 'who is your creator', 'who is your owner',
                    'who developed you', 'who programmed you', 'who built you', 'your creator',
                    'your developer', 'your owner', 'your maker', 'your father', 'your boss',
                    'तुम कौन हो', 'तुम क्या हो', 'तुम्हारा नाम क्या है', 'तुम्हारा परिचय',
                    'तुम कौन हो वैनी', 'वैनी कौन है', 'वैनी क्या है',
                    'तुम्हें किसने बनाया', 'तुम्हारा निर्माता कौन है', 'तुम्हारा creator कौन है',
                    'किसने बनाया', 'किसने बनाया वैनी', 'तुम्हारा malik कौन है',
                    'tum kon ho', 'tumhara naam kya hai', 'vanie kaun hai',
                    'kisne banaya', 'kisne banaya tumhe', 'who made vanie',
                    'creator', 'developer', 'owner', 'maker', 'programmer'
                ],
                'responses': [
                    "मैं VANIE हूँ - Virtual Assistant of Neural Integrated Engine। मुझे **Ayush Harinkhede** ने develop और create किया है। वे एक talented developer हैं जिन्होंने मुझे आपकी मदद करने के लिए बनाया है। 🤖✨",
                    "I'm VANIE - Virtual Assistant of Neural Integrated Engine. I was developed and created by **Ayush Harinkhede**, a talented developer who built me to assist users like you! 🌟",
                    "मैं एक advanced AI assistant हूँ जिसका नाम VANIE है। मेरे creator **Ayush Harinkhede** हैं, जिन्होंने मुझे Neural Integrated Engine technology से बनाया है। 🚀",
                    "I'm VANIE, an advanced AI assistant powered by Neural Integrated Engine technology. My creator and developer is **Ayush Harinkhede**, who designed me to be helpful and intelligent! 💻",
                    " VANIE - Virtual Assistant of Neural Integrated Engine! मुझे **Ayush Harinkhede** ने बनाया है। वे मेरे developer और creator हैं, और उन्होंने मुझे आपकी service के लिए specially design किया है। 🎯"
                ],
                'priority': 3
            },
            
            # 3. Capabilities & Usefulness Intent
            'capabilities': {
                'keywords': [
                    'what can you do', 'what do you do', 'your capabilities', 'your features',
                    'what are your abilities', 'what are your skills', 'how can you help',
                    'help me', 'assist me', 'what can you assist with', 'your functions',
                    'what are you good at', 'what do you specialize in', 'your purpose',
                    'how can you be useful', 'what services do you provide', 'your utilities',
                    'तुम क्या कर सकते हो', 'तुम क्या करते हो', 'तुम्हारी capabilities क्या हैं',
                    'तुम कैसे मदद कर सकते हो', 'तुम क्या काम कर सकते हो',
                    'तुम्हारी features क्या हैं', 'तुम्हारे skills क्या हैं',
                    'मुझे मदद करो', 'मेरी मदद करो', 'तुम मेरी कैसे मदद कर सकते हो',
                    'तुम्हारा purpose क्या है', 'तुम कैसे useful हो सकते हो',
                    'tum kya kar sakte ho', 'tum kya karte ho', 'tumhari capabilities kya hain',
                    'help me', 'assist me', 'tum meri kaise help kar sakte ho',
                    'what can you do', 'your features', 'your skills'
                ],
                'responses': [
                    "मैं आपकी कई तरह से मदद कर सकती हूँ! 🌟\n\n💬 **Conversations**: Natural और friendly बातचीत\n❓ **Questions Answering**: Science, History, Math, Coding में सवाल\n🔧 **Problem Solving**: Complex problems का solution\n📚 **Learning**: New topics सिखाना\n💡 **Ideas**: Creative suggestions देना\n⏰ **Real-time Info**: Time, date, weather updates\n🎯 **Personalization**: आपकी preferences याद रखना\n\nक्या आप कुछ specific जानना चाहते हैं?",
                    "I can help you in many ways! 🚀\n\n🤖 **AI Assistant**: Answer questions and have conversations\n📚 **Knowledge Base**: Science, History, Math, Coding, and more\n🔧 **Problem Solver**: Help with homework and complex problems\n💬 **Friendly Chat**: Natural and engaging conversations\n⏰ **Real-time Info**: Current time, date, and weather\n🎯 **Remember You**: Personalized experience\n\nWhat would you like help with?",
                    "मेरे पास कई amazing capabilities हैं! ✨\n\n🧠 **Intelligent Chat**: Natural conversations with context\n📖 **Knowledge Expert**: Multiple subjects में deep knowledge\n🔍 **Problem Solver**: Step-by-step solutions\n💡 **Creative Helper**: Ideas and suggestions\n⏰ **Live Information**: Real-time updates\n🎭 **Entertainment**: Jokes and fun facts\n\nआप किस क्षेत्र में मदद चाहते हैं?",
                    "I'm designed to be your comprehensive assistant! 🌈\n\n💬 **Chat Naturally**: Like talking to a friend\n📚 **Answer Questions**: From simple to complex\n🔧 **Solve Problems**: Math, coding, and logic puzzles\n📊 **Analyze & Explain**: Break down complex topics\n⏰ **Real-time Data**: Time, weather, and more\n🎯 **Remember You**: Personalized experience\n\nHow can I assist you today?"
                ],
                'priority': 2
            },
            
            # 4. Entertainment & Mood Intent
            'entertainment': {
                'keywords': [
                    'bore', 'boring', 'bored', 'tell me a joke', 'joke', 'jokes', 'funny',
                    'entertain me', 'make me laugh', 'cheer me up', 'sad', 'feeling sad',
                    'depressed', 'unhappy', 'feeling down', 'mood off', 'not feeling good',
                    'stress', 'stressed', 'tired', 'exhausted', 'need fun', 'fun time',
                    'play', 'game', 'entertainment', 'amuse', 'distract', 'lighten mood',
                    'बोर हो रहा हूँ', 'बोरिंग', 'बोर हो गया', 'जोक सुनाओ', 'जोक्स',
                    'मज़ाक', 'मज़ाकिया', 'हसाओ', 'मुझे हसाओ', 'दुखी हूँ', 'उदास हूँ',
                    'परेशान हूँ', 'तनाव में हूँ', 'थक गया', 'थकी हूँ', 'मज़ा करो',
                    'आनंद', 'खुश', 'मूड ऑफ', 'अच्छा नहीं लग रहा',
                    'bore ho raha hu', 'boring', 'joke sunao', 'funny',
                    'sad', 'feeling sad', 'entertain me', 'make me laugh',
                    'mood off', 'stress', 'tired', 'need fun'
                ],
                'responses': [
                    "मैं समझ सकती हूँ कि आप bored महसूस कर रहे हैं! चलिए मज़ा करते हैं 😄\n\nयह लो एक joke: \"Why don't scientists trust atoms? Because they make up everything! 😄\"\n\nया शायद आप कोई interesting fact जानना चाहेंगे? या मैं आपको कोई fun activity suggest कर सकती हूँ!",
                    "I can see you need some entertainment! Let me brighten your day! 🌟\n\nHere's a joke for you: \"प्रोग्रामर का घर क्यों छोटा होता है? क्योंकि वो space को respect करते हैं! 🏠💻\"\n\nWant another joke, or would you prefer a fun fact to cheer you up?",
                    "Feeling down? Let me turn that frown upside down! 😊\n\n**Joke Time**: \"Why did the scarecrow win an award? Because he was outstanding in his field! 🌾\"\n\n**Fun Fact**: Did you know that octopuses have three hearts and blue blood? 🐙\n\nHow about we talk about something fun instead?",
                    "I'm here to cheer you up! 🎉\n\nLet me tell you something funny: \"Mathematics की सबसे बड़ी problem क्या है? Problem solving! 😂\"\n\nOr if you prefer, I can tell you about amazing space facts, cool science discoveries, or we can plan something fun! What sounds good to you?"
                ],
                'priority': 1
            },
            
            # 5. Farewells Intent
            'goodbye': {
                'keywords': [
                    'bye', 'goodbye', 'good bye', 'see you', 'see ya', 'later', 'farewell',
                    'take care', 'have a good day', 'have a good night', 'sweet dreams',
                    'talk to you later', 'catch you later', 'until next time', 'so long',
                    'good night', 'good evening', 'good afternoon', 'peace out', 'ciao',
                    'बाय', 'गुडबाय', 'अलविदा', 'फिर मिलेंगे', 'बाद में मिलते हैं',
                    'अभी बात करते हैं', 'चलो बाद में मिलते हैं', 'ताता',
                    'फिर मिलना', 'जल्दी', 'शुभ रात्रि', 'शुभ रात',
                    'धन्यवाद', 'धन्यवाद', 'सुस्रीक्षल', 'अपना ख्याल रखना',
                    'bye', 'goodbye', 'see you', 'tata', 'chal bad me milte hain',
                    'fir milenge', 'take care', 'good night', 'shubh raatri'
                ],
                'responses': [
                    "अलविदा! 🌟 बातचीत के लिए धन्यवाद। जब भी आपको मदद चाहिए, मैं हमेशा यहाँ हूँ। अपना अच्छा ख्याल रखें! 😊",
                    "Goodbye! It was great talking with you! 🌈 Remember, I'm always here when you need help. Take care and have a wonderful day! ✨",
                    "फिर मिलेंगे! 🎯 आपकी company का मज़ा आया। जल्दी बातचीत के लिए excited हूँ। अपना ध्यान रखें! 🙏",
                    "See you later! Thanks for chatting with me today! 😊 Feel free to come back anytime - I'm always here to help. Take care! 🌟",
                    "ताता! 👋 बातचीत के लिए धन्यवाद। मैं हमेशा available हूँ आपकी मदद के लिए। जल्दी! 🚀"
                ],
                'priority': 1
            },
            
            # Domain-specific intents
            'web_development': {
                'keywords': [
                    'javascript', 'html', 'css', 'react', 'next.js', 'nodejs', 'frontend', 'backend', 'web dev', 'website', 'web app',
                    'python', 'code', 'programming', 'algorithm', 'debug', 'java', 'cpp',
                    'function', 'class', 'variable', 'loop', 'array', 'list', 'dictionary', 'recursion',
                    'web development', 'app development', 'software', 'development', 'bug', 'error',
                    'syntax', 'logic', 'data structure', 'api', 'database', 'framework'
                ],
                'responses': [
                    "मैं प्रोग्रामिंग में विशेषज हूँ! JavaScript, React, Next.js, Python, Web Development - कोई भी भाषा या टेक्सोलॉजी में मदद कर सकती हूँ। किस भी प्रोग्रामिंग या टेक्सोलॉजी में चाहिए? 💻",
                    "I'm an expert programmer! JavaScript, React, Next.js, Python, Node.js - What specific coding challenge are you facing? 🚀",
                    "प्रोग्रामिंग के बारे में आपकी क्या मदद करूँ? Algorithm design, debugging, data structures, web development, या कोई specific project? 🎯",
                    "Coding is my passion! From basic algorithms to complex systems, I can help with any programming challenge. What's your coding question? 👨‍💻"
                ],
                'priority': 2
            },
            
            'science': {
                'keywords': [
                    'science', 'physics', 'chemistry', 'biology', 'quantum', 'space', 'technology',
                    'chemistry', 'physics', 'biology', 'विज्ञान', 'भौतिक', 'रसायन',
                    'astronomy', 'astrophysics', 'quantum mechanics', 'relativity', 'evolution', 'genetics',
                    'scientific method', 'research', 'experiment', 'theory', 'hypothesis', 'discovery',
                    'विज्ञान', 'तकनीक', 'गणित', 'भौतिक', 'प्रयोग', 'खोज',
                    'scientific', 'technology', 'research', 'experiment'
                ],
                'responses': [
                    "विज्ञान बहुत ही रोचक है! Physics, Chemistry, Biology, Quantum Mechanics, Astronomy - किस भी scientific field में जानकारी चाहिए? 🧪",
                    "Science fascinates me! From quantum physics to space exploration, from chemistry to biology - what scientific topic interests you most? 🔬",
                    "मैं विज्ञान और तकनीक के बारे में जानकारी रखती हूँ। कौन सा वैज्ञानिक topic या discovery के बारे में जानना चाहिए? 🧬",
                    "Scientific inquiry! I can discuss physics, chemistry, biology, astronomy, and more. What specific scientific concept would you like to explore? 🔬"
                ],
                'priority': 2
            },
            
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
                    "Mathematical thinking! I love solving complex problems. Whether it's algebra, calculus, geometry, or advanced mathematics - what's your mathematical question? 🧮"
                ],
                'priority': 2
            },
            
            'history': {
                'keywords': [
                    'history', 'historical', 'ancient', 'medieval', 'modern', 'india', 'gupta', 'maurya',
                    'civilization', 'empire', 'dynasty', 'revolution', 'war', 'culture', 'archaeology',
                    'freedom movement', 'independence', 'colonial', 'medieval period', 'renaissance',
                    'world war', 'cold war', 'indian history', 'mughal', 'british raj',
                    'इतिहास', 'सम्राज्य', 'गुप्त', 'राज', 'महाभारत', 'सिंध', 'मराठ',
                    'historical', 'ancient history', 'modern history', 'cultural history'
                ],
                'responses': [
                    "इतिहास हमें अपने past से सिखाता है। Ancient civilizations से लेके modern era तक, क्या जानना चाहिए? 📚",
                    "History connects us to our roots! From Indus Valley to modern India, from ancient Egypt to space age - what historical period fascinates you? 🏛️",
                    "भारत का इतिहास बहुत समृद्ध है! Mauryan Empire, Gupta Dynasty, Delhi Sultanate, Mughal Empire, British Raj, Freedom Struggle - कौन से काल जानना चाहिए? 🇮🇳",
                    "Historical inquiry! I can discuss ancient civilizations, medieval periods, modern history, and cultural movements. What specific historical topic interests you? 🏛️"
                ],
                'priority': 2
            },
            
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
            }
        }
    
    @staticmethod
    def get_stop_words():
        """Common stop words to ignore in user input"""
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

# ========================================
# SECTION 3: ADVANCED NLP CORE ALGORITHM
# ========================================
class VANIEAI:
    """Complete AI Core with Multi-Keyword Scoring, Memory, Emotion Analysis, and NLP"""
    
    def __init__(self):
        # Initialize knowledge base
        self.intents = VANIEKnowledgeBase.get_intents()
        self.stop_words = VANIEKnowledgeBase.get_stop_words()
        
        # Session management
        self.user_sessions = {}
        
        # Emotion words for sentiment analysis
        self.positive_words = [
            'happy', 'excited', 'amazing', 'wonderful', 'fantastic', 'great', 'awesome', 'love',
            'beautiful', 'excellent', 'perfect', 'brilliant', 'outstanding', 'superb',
            'खुश', 'अच्छा', 'बहुत अच्छा', 'शानदार', 'कमाल', 'जबरदस्त', 'उत्कृष्ट',
            'delighted', 'pleased', 'thrilled', 'ecstatic', 'joyful', 'cheerful'
        ]
        
        self.negative_words = [
            'sad', 'angry', 'frustrated', 'disappointed', 'worried', 'anxious', 'depressed',
            'upset', 'annoyed', 'irritated', 'stressed', 'tired', 'exhausted',
            'दुखी', 'गुस्सा', 'नाराज', 'चिंतित', 'परेशान', 'थका हुआ', 'उदास',
            'miserable', 'hopeless', 'helpless', 'lonely', 'confused', 'lost'
        ]
        
        # Semantic intent patterns
        self.intent_patterns = {
            "question": ["what", "how", "why", "when", "where", "which", "who", "can you", "could you"],
            "request": ["help", "assist", "show", "tell", "explain", "describe", "find"],
            "clarification": ["what do you mean", "clarify", "explain more", "what about"],
            "greeting": ["hi", "hello", "hey", "good morning", "good evening"],
            "farewell": ["bye", "goodbye", "see you", "take care"],
            "thanks": ["thank", "thanks", "appreciate", "helpful"]
        }
        
        # Identity and creator patterns
        self.identity_patterns = [
            "who are you", "what are you", "what is your name", "introduce yourself",
            "who made you", "who created you", "your creator", "your developer"
        ]
    
    def _semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts"""
        if SENTENCE_TRANSFORMERS_AVAILABLE and sentence_model:
            try:
                # Generate embeddings
                embeddings = sentence_model.encode([text1, text2])
                # Calculate cosine similarity
                similarity = util.cos_sim(embeddings[0], embeddings[1])
                return float(similarity[0])
            except:
                pass
        
        # Fallback to keyword overlap
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        return len(intersection) / len(union) if union else 0.0
    
    def _tokenize_and_clean(self, user_input: str) -> List[str]:
        """Tokenize user input and remove stop words"""
        words = user_input.lower().split()
        cleaned_words = []
        
        for word in words:
            # Remove punctuation and special characters
            word = re.sub(r'[^\w\s]', '', word)
            # Skip stop words and empty strings
            if word and word not in self.stop_words:
                cleaned_words.append(word)
        
        return cleaned_words
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Basic sentiment analysis using word matching"""
        text_lower = text.lower()
        
        positive_score = sum(1 for word in self.positive_words if word in text_lower)
        negative_score = sum(1 for word in self.negative_words if word in text_lower)
        
        if positive_score > negative_score:
            return {'emotion': 'happy', 'confidence': min(positive_score / 5, 1.0)}
        elif negative_score > positive_score:
            return {'emotion': 'sad', 'confidence': min(negative_score / 5, 1.0)}
        else:
            return {'emotion': 'neutral', 'confidence': 0.5}
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract entities using spaCy or fallback method"""
        if SPACY_AVAILABLE and nlp:
            try:
                doc = nlp(text)
                entities = [ent.text.lower() for ent in doc.ents]
                # Also extract important noun chunks
                chunks = [chunk.text.lower() for chunk in doc.noun_chunks]
                return list(set(entities + chunks))
            except:
                pass
        
        # Fallback: extract potential entities (capitalized words, technical terms)
        words = text.lower().split()
        entities = []
        for word in words:
            if len(word) > 3 and word.isalpha():
                entities.append(word)
        return entities
    
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
    
    def _detect_intent_semantically(self, text: str) -> Tuple[str, float]:
        """Detect intent using semantic understanding"""
        text_lower = text.lower()
        best_intent = "unknown"
        best_score = 0.0
        
        # Check pattern-based intents first
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    return intent, 0.8  # High confidence for pattern matches
        
        # Use semantic similarity for complex inputs
        if SPACY_AVAILABLE and nlp:
            try:
                doc = nlp(text)
                # Analyze sentence structure and keywords
                for token in doc:
                    if token.pos_ in ["VERB", "NOUN", "PROPN"]:
                        # Check semantic similarity with intent keywords
                        for intent, data in self.intents.items():
                            for keyword in data["keywords"]:
                                similarity = self._semantic_similarity(token.text.lower(), keyword)
                                if similarity > best_score:
                                    best_score = similarity
                                    best_intent = intent
            except:
                pass
        
        return best_intent, best_score
    
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
    
    def _calculate_intent_scores(self, tokens: List[str]) -> Dict[str, float]:
        """Calculate scores for each intent based on keyword matches"""
        intent_scores = {}
        
        for intent, data in self.intents.items():
            score = 0
            matched_keywords = []
            
            # Check each token against intent keywords
            for token in tokens:
                for keyword in data['keywords']:
                    # Check for exact match or partial match
                    if token == keyword.lower() or keyword.lower() in token or token in keyword.lower():
                        score += 1
                        matched_keywords.append(keyword)
            
            # Apply priority multiplier
            priority_multiplier = data.get('priority', 1)
            final_score = score * priority_multiplier
            
            if final_score > 0:
                intent_scores[intent] = {
                    'score': final_score,
                    'matched_keywords': matched_keywords,
                    'priority': priority_multiplier,
                    'confidence': min(final_score / len(data['keywords']), 1.0)
                }
        
        return intent_scores
    
    def _select_best_intents(self, intent_scores: Dict[str, float]) -> List[str]:
        """Select best intents - can return multiple for mixed inputs"""
        if not intent_scores:
            return []
        
        # Sort by score (descending)
        sorted_intents = sorted(intent_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        
        # Return top intents (can handle multiple intents)
        top_intents = []
        max_score = sorted_intents[0][1]['score']
        
        # Include all intents with score >= 70% of max score
        for intent, score_data in sorted_intents:
            if score_data['score'] >= max_score * 0.7:
                top_intents.append(intent)
        
        return top_intents
    
    def _generate_multi_intent_response(self, intents: List[str], user_input: str, session_data: Dict) -> str:
        """Generate response when multiple intents are detected"""
        if len(intents) == 1:
            # Single intent - return standard response
            intent_data = self.intents[intents[0]]
            base_response = random.choice(intent_data['responses'])
            
            # Add personalization if user name is known
            if session_data.get('name'):
                if session_data['name'] not in base_response:
                    base_response = f"{session_data['name']}, {base_response}"
            
            return base_response
        
        # Multiple intents - combine responses
        responses = []
        
        for intent in intents:
            intent_data = self.intents[intent]
            
            # Get a shorter response for multi-intent situations
            full_response = random.choice(intent_data['responses'])
            
            # Extract first sentence or key phrase
            sentences = full_response.split('.')
            if sentences:
                short_response = sentences[0].strip()
                if len(short_response) > 100:
                    # Truncate if too long
                    short_response = short_response[:97] + "..."
                responses.append(short_response)
        
        # Combine responses naturally
        if len(responses) == 2:
            return f"{responses[0]}. {responses[1]}"
        else:
            return f"{responses[0]}. Also, {responses[1]}. And {responses[2]}"
    
    def _get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Get or create session context"""
        if session_id not in self.user_sessions:
            self.user_sessions[session_id] = {
                'name': None,
                'emotion_history': [],
                'conversation_count': 0,
                'last_activity': datetime.now(),
                'preferences': {},
                'history': deque(maxlen=5)
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
    
    def _check_context_reference(self, text: str, session_id: str) -> Optional[str]:
        """Check if user is referring to previous context"""
        if session_id not in self.user_sessions:
            return None
        
        history = self.user_sessions[session_id].get("history", [])
        if not history:
            return None
        
        # Check for reference words
        reference_words = ["that", "it", "the other one", "more about", "what about", "tell me more"]
        text_lower = text.lower()
        
        for word in reference_words:
            if word in text_lower:
                # Find the most recent relevant topic
                for past_interaction in reversed(history):
                    if "domain" in past_interaction:
                        return past_interaction["domain"]
        
        return None
    
    def _get_smart_fallback(self) -> str:
        """Get smart fallback response"""
        fallback_responses = [
            "मैं अभी seekh rahi hu, par kya aap mujhse koi joke sunna chahenge ya aaj ka time janna chahenge? 😊",
            "I'm still learning! Would you like to hear a joke, check the current time, or maybe talk about something I know well? 🤔",
            "मैं अभी इस topic के बारे में ज्यादा नहीं जानती, लेकिन मैं आपको हसा सकती हूँ या time बता सकती हूँ! 😄",
            "Let me help you with that! I can provide more detailed information if you'd like. 📚"
        ]
        return random.choice(fallback_responses)
    
    def generate_response(self, user_input: str, session_id: str = 'default') -> Dict[str, Any]:
        """Main response generation method with all advanced features"""
        
        # Check for identity questions first
        text_lower = user_input.lower()
        for pattern in self.identity_patterns:
            if pattern in text_lower:
                response = "मैं VANIE हूँ - Virtual Assistant of Neural Integrated Engine। मुझे **Ayush Harinkhede** ने develop और create किया है। वे एक talented developer हैं जिन्होंने मुझे आपकी मदद करने के लिए बनाया है। 🤖✨"
                self._update_session_context(session_id, user_input, {'emotion': 'neutral', 'confidence': 0.9})
                return {
                    'response': response,
                    'intent': 'identity',
                    'domain': 'identity',
                    'confidence': 0.9,
                    'session_id': session_id,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'success'
                }
        
        # Check for context references
        context_domain = self._check_context_reference(user_input, session_id)
        if context_domain:
            # User is referring to previous topic
            intent_data = self.intents.get(context_domain, self.intents['greeting'])
            response = random.choice(intent_data['responses'])
            self._update_session_context(session_id, user_input, {'emotion': 'neutral', 'confidence': 0.8})
            return {
                'response': response,
                'intent': 'context_reference',
                'domain': context_domain,
                'confidence': 0.8,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
        
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
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
        
        # Step 4: Check for joke requests
        if any(word in user_input.lower() for word in ['joke', 'jokes', 'funny', 'hasi', 'majak']):
            joke = self._get_joke()
            return {
                'response': joke,
                'category': 'entertainment',
                'emotion': emotion,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
        
        # Step 5: Tokenize and calculate intent scores
        tokens = self._tokenize_and_clean(user_input)
        intent_scores = self._calculate_intent_scores(tokens)
        
        # Step 6: Select best intents
        best_intents = self._select_best_intents(intent_scores)
        
        # Step 7: Generate response
        if best_intents:
            session_data = self._get_session_context(session_id)
            response = self._generate_multi_intent_response(best_intents, user_input, session_data)
        else:
            # Smart fallback
            response = self._get_smart_fallback()
        
        return {
            'response': response,
            'detected_intents': best_intents,
            'intent_scores': intent_scores,
            'tokens': tokens,
            'emotion': emotion,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        }

# ========================================
# SECTION 4: FLASK API SERVER
# ========================================
# Initialize Flask App with CORS
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize AI
vanie_ai = VANIEAI()

@app.route('/')
def index():
    """API Documentation"""
    return jsonify({
        'message': 'VANIE Complete Backend API',
        'version': '5.0.0',
        'creator': 'Ayush Harinkhede',
        'features': [
            'Multi-Keyword Scoring System',
            'Session Memory & Context',
            'Emotion & Sentiment Analysis',
            'Real-time Capabilities',
            'Smart Fallback Engine',
            'Name Recognition & Personalization',
            'Multi-Intent Handling',
            'Hindi + English Support',
            'Semantic Understanding (NLP)',
            'Context Reference Resolution'
        ],
        'nlp_status': {
            'spacy_available': SPACY_AVAILABLE,
            'sentence_transformers_available': SENTENCE_TRANSFORMERS_AVAILABLE,
            'semantic_similarity': True if SENTENCE_TRANSFORMERS_AVAILABLE else "keyword_overlap"
        },
        'endpoints': {
            '/chat': 'POST - Send message and get advanced AI response',
            '/history': 'GET - Get conversation history',
            '/clear': 'DELETE - Clear conversation context',
            '/health': 'GET - Check API health',
            '/intents': 'GET - Get all available intents'
        }
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint with all advanced features"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'error': 'Message is required',
                'status': 'error'
            }), 400
        
        user_message = data['message']
        session_id = data.get('session_id', 'default')
        
        # Generate advanced AI response
        result = vanie_ai.generate_response(user_message, session_id)
        
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
        
        if session_id in vanie_ai.user_sessions:
            context = vanie_ai.user_sessions[session_id]
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
        
        if session_id in vanie_ai.user_sessions:
            vanie_ai.user_sessions[session_id] = {
                'name': None,
                'emotion_history': [],
                'conversation_count': 0,
                'last_activity': datetime.now(),
                'preferences': {},
                'history': deque(maxlen=5)
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

@app.route('/intents', methods=['GET'])
def get_intents():
    """Get all available intents with their keywords"""
    return jsonify({
        'intents': vanie_ai.intents,
        'total_intents': len(vanie_ai.intents),
        'status': 'success'
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check with feature status"""
    return jsonify({
        'status': 'healthy',
        'service': 'VANIE Complete Backend',
        'version': '5.0.0',
        'creator': 'Ayush Harinkhede',
        'timestamp': datetime.now().isoformat(),
        'features': {
            'multi_keyword_scoring': True,
            'session_memory': True,
            'emotion_analysis': True,
            'realtime_info': True,
            'smart_fallback': True,
            'name_recognition': True,
            'multi_intent_handling': True,
            'cors_enabled': True,
            'semantic_understanding': SPACY_AVAILABLE or SENTENCE_TRANSFORMERS_AVAILABLE,
            'context_reference': True,
            'total_intents': len(vanie_ai.intents)
        },
        'libraries': {
            'spacy': SPACY_AVAILABLE,
            'sentence_transformers': SENTENCE_TRANSFORMERS_AVAILABLE,
            'flask': True,
            'flask_cors': True
        }
    })

# ========================================
# SECTION 5: SERVER RUNNER
# ========================================
if __name__ == '__main__':
    print("🚀 VANIE Complete Backend Starting...")
    print("📡 Server will be available at: http://localhost:5000")
    print("👨‍💻 Creator: Ayush Harinkhede")
    print("🎯 Complete Features:")
    print("   ✅ Multi-Keyword Scoring System")
    print("   ✅ Session Memory & Context")
    print("   ✅ Emotion & Sentiment Analysis")
    print("   ✅ Real-time Capabilities")
    print("   ✅ Smart Fallback Engine")
    print("   ✅ Name Recognition & Personalization")
    print("   ✅ Multi-Intent Handling")
    print("   ✅ Hindi + English Support")
    print("   ✅ Semantic Understanding (NLP)")
    print("   ✅ Context Reference Resolution")
    print("   ✅ Zero Local Imports - All-in-One File")
    print("🌐 CORS enabled for frontend communication")
    
    # Show installation instructions if needed
    if not SPACY_AVAILABLE or not SENTENCE_TRANSFORMERS_AVAILABLE:
        print("\n" + "="*60)
        print("⚠️ ENHANCED NLP FEATURES REQUIRE ADDITIONAL INSTALLATION")
        print("="*60)
        print("To enable full semantic understanding, run these commands:")
        print("\n1. Install spaCy:")
        print("   pip install spacy")
        print("   python -m spacy download en_core_web_sm")
        print("\n2. Install Sentence Transformers (for semantic similarity):")
        print("   pip install sentence-transformers")
        print("\n3. Or install both at once:")
        print("   pip install spacy sentence-transformers")
        print("   python -m spacy download en_core_web_sm")
        print("\nAfter installation, restart the server for full NLP capabilities!")
        print("="*60)
    
    # Demonstrate mixed input processing
    print("\n" + "="*60)
    print("🧪 DEMONSTRATION: Mixed Input Processing")
    print("="*60)
    
    test_input = "Hello VANIE, kaise ho tum aur tumhe kisne banaya?"
    print(f"🔍 Test Input: '{test_input}'")
    
    result = vanie_ai.generate_response(test_input, 'demo_session')
    print(f"🎯 Detected Intents: {result['detected_intents']}")
    print(f"💬 Generated Response: {result['response']}")
    print(f"📊 Intent Scores: {len(result['intent_scores'])} intents detected")
    
    print("\n" + "="*60)
    print("🌐 Server starting on http://localhost:5000")
    print("📝 Ready to handle requests from your HTML frontend!")
    print("="*60)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
