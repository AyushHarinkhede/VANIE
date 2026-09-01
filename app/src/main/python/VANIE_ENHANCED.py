#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VANIE - Virtual Assistant of Neural Integrated Engine
ENHANCED VERSION WITH ADVANCED ALGORITHMS & CONVERSATION

Features:
- Advanced sentiment analysis
- Context-aware conversation with memory
- Multi-turn conversation support
- Intent classification with confidence scores
- Joke/Riddle/Trivia support
- Advanced NLP algorithms
- User personality detection
- Conversation analytics
- Learning from interactions

REQUIREMENTS:
flask==2.3.3
flask-cors==4.0.0
psutil==5.9.5
requests==2.31.0

INSTALLATION:
pip install flask flask-cors psutil requests

RUN:
python VANIE_ENHANCED.py
Then visit: http://localhost:5000
"""

import os
import sys
import json
import datetime
import platform
import socket
import subprocess
import threading
import time
import re
import calendar

try:
    import psutil
except ImportError:
    psutil = None

try:
    import requests
except ImportError:
    requests = None

try:
    from flask import Flask, request, jsonify, render_template, send_from_directory
    from flask_cors import CORS
except ImportError:
    Flask = None
    CORS = None
import logging
from typing import Dict, Any, List, Tuple
import random
import math
import hashlib
import base64
import uuid
from collections import Counter, defaultdict
from difflib import SequenceMatcher
import statistics
import heapq
from functools import lru_cache
import operator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app if available
if Flask is not None:
    app = Flask(__name__, static_folder='.', static_url_path='')
    if CORS is not None:
        CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"]}})
else:
    app = None

class AdvancedNLPAlgorithms:
    """Advanced Natural Language Processing Algorithms"""
    
    @staticmethod
    def calculate_sentiment(text: str) -> Tuple[str, float]:
        """
        Calculate sentiment of text using multiple approaches
        Returns: (sentiment, confidence)
        """
        text_lower = text.lower()
        
        positive_words = {
            'good': 2, 'great': 3, 'excellent': 3, 'amazing': 3, 'wonderful': 3,
            'perfect': 3, 'love': 2, 'like': 1, 'happy': 2, 'excited': 2,
            'awesome': 3, 'fantastic': 3, 'brilliant': 3, 'beautiful': 2,
            'best': 3, 'nice': 1, 'cool': 1, 'interesting': 1, 'fun': 1,
            'खुश': 2, 'शानदार': 3, 'बढ़िया': 2, 'अच्छा': 1, 'सुंदर': 2
        }
        
        negative_words = {
            'bad': 2, 'terrible': 3, 'awful': 3, 'horrible': 3, 'hate': 3,
            'dislike': 2, 'sad': 2, 'upset': 2, 'angry': 2, 'frustrated': 2,
            'worst': 3, 'poor': 2, 'boring': 1, 'stupid': 2, 'annoying': 2,
            'बुरा': 2, 'भयानक': 3, 'दुःख': 2, 'गुस्सा': 2, 'परेशान': 2
        }
        
        intensity_multiplier = {
            'very': 1.5, 'really': 1.5, 'extremely': 2, 'absolutely': 2,
            'so': 1.3, 'way': 1.3, 'quite': 1.2, 'बहुत': 1.5, 'अत्यधिक': 2
        }
        
        # Tokenize and calculate scores
        words = text_lower.split()
        sentiment_score = 0
        confidence = 0
        intensity = 1.0
        
        for word in words:
            if word in intensity_multiplier:
                intensity = intensity_multiplier[word]
            elif word in positive_words:
                sentiment_score += positive_words[word] * intensity
                confidence += 1
                intensity = 1.0
            elif word in negative_words:
                sentiment_score -= negative_words[word] * intensity
                confidence += 1
                intensity = 1.0
        
        if confidence == 0:
            return 'neutral', 0.5
        
        # Normalize confidence (0-1)
        confidence = min(confidence / len(words), 1.0)
        
        if sentiment_score > 0:
            return 'positive', min(abs(sentiment_score) / (len(words) + 1), 1.0)
        elif sentiment_score < 0:
            return 'negative', min(abs(sentiment_score) / (len(words) + 1), 1.0)
        else:
            return 'neutral', confidence
    
    @staticmethod
    def extract_keywords(text: str, top_n: int = 5) -> List[str]:
        """Extract top keywords from text"""
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'is', 'are', 'was', 'were', 'be', 'have', 'has', 'do', 'does',
            'मैं', 'आप', 'है', 'हैं', 'में', 'को', 'का', 'की', 'से', 'और'
        }
        
        words = re.findall(r'\b\w+\b', text.lower())
        filtered = [w for w in words if w not in stop_words and len(w) > 2]
        
        word_freq = Counter(filtered)
        return [word for word, _ in word_freq.most_common(top_n)]
    
    @staticmethod
    def calculate_text_similarity(text1: str, text2: str) -> float:
        """Calculate similarity between two texts (0-1)"""
        words1 = set(re.findall(r'\b\w+\b', text1.lower()))
        words2 = set(re.findall(r'\b\w+\b', text2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    @staticmethod
    def correct_spelling(word: str, word_list: List[str]) -> str:
        """Find closest match for misspelled word"""
        if len(word_list) == 0:
            return word
        
        closest = min(word_list, key=lambda x: SequenceMatcher(None, word, x).ratio())
        return closest
    
    @staticmethod
    def extract_numbers(text: str) -> List[float]:
        """Extract all numbers from text"""
        numbers = re.findall(r'[-+]?\d+\.?\d*', text)
        return [float(n) for n in numbers]
    
    @staticmethod
    def detect_intent_with_confidence(text: str, patterns: Dict[str, str]) -> Tuple[str, float]:
        """Detect intent with confidence score"""
        text_lower = text.lower()
        best_intent = 'general'
        best_score = 0.0
        
        for intent, pattern in patterns.items():
            matches = re.findall(pattern, text_lower)
            if matches:
                # Score based on number of matches and match length
                score = min(len(matches) * 0.3 + 0.7, 1.0)
                if score > best_score:
                    best_score = score
                    best_intent = intent
        
        return best_intent, best_score


class ConversationMemory:
    """Advanced conversation history and memory management"""
    
    def __init__(self, max_history: int = 20):
        self.conversation_history = []
        self.user_context = {}
        self.max_history = max_history
        self.session_start = datetime.datetime.now()
        self.user_name = "Guest"
        self.interaction_count = 0
        
    def add_message(self, role: str, content: str, intent: str = None, metadata: Dict = None):
        """Add message to conversation history"""
        message = {
            'timestamp': datetime.datetime.now().isoformat(),
            'role': role,
            'content': content,
            'intent': intent,
            'metadata': metadata or {}
        }
        self.conversation_history.append(message)
        
        if len(self.conversation_history) > self.max_history:
            self.conversation_history.pop(0)
        
        if role == 'user':
            self.interaction_count += 1
    
    def get_context(self, lookback: int = 5) -> List[Dict]:
        """Get recent conversation context"""
        return self.conversation_history[-lookback:]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get conversation summary"""
        user_messages = [m for m in self.conversation_history if m['role'] == 'user']
        bot_messages = [m for m in self.conversation_history if m['role'] == 'bot']
        
        return {
            'total_messages': len(self.conversation_history),
            'user_messages': len(user_messages),
            'bot_messages': len(bot_messages),
            'session_duration': str(datetime.datetime.now() - self.session_start),
            'interaction_count': self.interaction_count
        }


class VANIEEnhanced:
    """Enhanced VANIE Engine with Advanced Algorithms"""
    
    def __init__(self):
        self.nlp = AdvancedNLPAlgorithms()
        self.memory = ConversationMemory()
        self.user_name = "Guest"
        self.weather_cache = {}
        self.system_info_cache = None
        self.last_system_update = 0
        self.uptime_start = time.time()
        self.user_profiles = defaultdict(dict)
        
        self.knowledge_base = self._initialize_knowledge_base()
        self._initialize_conversation_data()
    
    def _initialize_knowledge_base(self) -> Dict[str, Any]:
        """Initialize comprehensive knowledge base"""
        return {
            'vanie_info': {
                'full_form': 'Virtual Assistant of Neural Integrated Engine',
                'creator': 'Ayush Harinkhede',
                'version': '3.0-ENHANCED',
                'capabilities': [
                    'Advanced sentiment analysis',
                    'Context-aware conversations',
                    'Multi-turn dialogue',
                    'Joke and riddle generation',
                    'Trivia questions',
                    'Advanced NLP algorithms',
                    'User personality detection',
                    'Conversation analytics',
                    'Real-time system monitoring',
                    'Programming assistance'
                ]
            },
            'intent_patterns': {
                'greeting': r'(नमस्ते|hello|hi|hey|कैसे हो|what\'s up|greetings|welcome)',
                'help': r'(help|मदद|सहायता|assistance|support)',
                'bye': r'(bye|अलविदा|goodbye|बाय|see you|farewell)',
                'thanks': r'(thanks|धन्यवाद|शुक्रिया|thank you)',
                'time': r'(time|समय|बजा|current time|अभी|what time)',
                'date': r'(date|तारीख|आज|when|calendar)',
                'weather': r'(weather|मौसम|temperature|तापमान|rain)',
                'system': r'(system|computer|pc|कंप्यूटर|memory|cpu|specs)',
                'vanie': r'(vanie|तुम कौन|who are you|आपका नाम|about|yourself)',
                'math': r'(\d+\.?\d*\s*[\+\-\*/%\^]\s*\d+\.?\d*|calculate|sqrt|square root|sin|cos|tan|log|ln|fact|factorial|percent|%)',
                'code': r'(code|python|javascript|java|cpp|प्रोग्रामिंग|programming)',
                'emotional': r'(feeling|sad|happy|excited|stressed|anxious|angry|gussa|bore|उदास|खुश|परेशान)',
                'routine_morning': r'(good morning|सुप्रभात|good morning vanie|morning talk)',
                'routine_night': r'(good night|शुभ रात्रि|sweet dreams|so jao)',
                'routine_food': r'(khana khaya|breakfast|lunch|dinner|chai|coffee|food|what did you eat)',
                'routine_meetup': r'(meetup|milte hain|let\'s meet|chalo milte|hangout|kahin chalein|meet up)',
                'routine_daily': r'(daily routine|aaj ka plan|what are you doing|kya kar rahe ho|kya chal raha hai)',
                'emotions_happy': r'(happy|excited|awesome|good news|खुश|मज़ा आ गया|great day)',
                'emotions_sad': r'(sad|lonely|depressed|heartbroken|उदास|अकेला|upset|cry)',
                'emotions_stress': r'(stressed|anxious|tired|thak gaya|headache|tension|परेशान)',
                'emotions_angry': r'(angry|frustrated|gussa|annoyed|irritated|गुस्सा)',
                'emotions_bored': r'(bored|boring|bore ho raha|kuch batao|kuch bolo)',
                'age_calc': r'(age|umar|birthdate|born in|date of birth|dob|kitne saal)',
                'joke': r'(joke|मजाक|हंसाओ|funny|laugh|चुटकुले)',
                'riddle': r'(riddle|पहेली|guess|सवाल)',
                'trivia': r'(trivia|क्विज़|facts|interesting|fact)',
                'game': r'(game|खेल|play|word game)',
                'motivation': r'(motivation|inspire|courage|strength|confidence|प्रेरणा)',
                'quote': r'(quote|famous|कहावत|wisdom|advice)',
                'conversion': r'(convert|conversion|transform|unit|km|mile|celsius|fahrenheit|kg|lbs|gb|mb)',
                'search': r'(search|find|look for|खोजो)',
                'torch_on': r'(torch on|flashlight on|flash on|लाइट चालू|लाइट ऑन|टॉर्च ऑन|टॉर्च चालू)',
                'torch_off': r'(torch off|flashlight off|flash off|लाइट बंद|लाइट ऑफ|टॉर्च ऑफ|टॉर्च बंद)',
                'wifi_on': r'(wifi on|turn on wifi|enable wifi|वाईफाई ऑन|वाईफाई चालू)',
                'wifi_off': r'(wifi off|turn off wifi|disable wifi|वाईफाई ऑफ|वाईफाई बंद)',
                'bluetooth_on': r'(bluetooth on|turn on bluetooth|enable bluetooth|ब्लूटूथ ऑन|ब्लूटूथ चालू)',
                'bluetooth_off': r'(bluetooth off|turn off bluetooth|disable bluetooth|ब्लूटूथ ऑफ|ब्लूटूथ बंद)',
                'dnd_on': r'(dnd on|do not disturb on|डीएनडी चालू|डिस्टर्ब न करें)',
                'dnd_off': r'(dnd off|do not disturb off|डीएनडी बंद)',
                'mode_silent': r'(silent mode|phone silent|साइलेंट मोड|साइलेंट करो)',
                'mode_vibrate': r'(vibrate mode|phone vibrate|वाइब्रेट मोड|वाइब्रेट करो)',
                'mode_ring': r'(ring mode|normal mode|रिंग मोड|रिंगर ऑन)',
                'make_call': r'(call|make a call|dial|फोन करो|कॉल करो|कॉल लगाओ)',
                'send_sms': r'(text|send text|send sms|message|मैसेज करो|एसएमएस भेजो)',
                'send_whatsapp': r'(whatsapp|send whatsapp|व्हाट्सएप करो|व्हाट्सएप मैसेज)',
                'answer_call': r'(pickup call|receive call|answer call|कॉल उठाओ|कॉल पिकअप|पिकअप करो)',
                'reject_call': r'(cut call|hangup|reject call|end call|कॉल काटो|कॉल कट|कॉल रिजेक्ट)',
            }
        }
    
    def _initialize_conversation_data(self):
        """Initialize conversation data"""
        self.jokes = [
            {"joke": "Why did the Python programmer go broke? Because he lost his class!"},
            {"joke": "How many programmers does it take to change a light bulb? None, that's a hardware problem!"},
            {"joke": "Why do programmers prefer dark mode? Because light attracts bugs!"},
            {"joke": "क्या आप जानते हैं? AI को भी कभी-कभी hang हो जाता है... जब उसे अपने सॉकेट का पता न चले! 😄"},
            {"joke": "एक आदमी ने डॉक्टर से पूछा: मेरा कंप्यूटर सिर्फ फिल्मों में काम करता है। डॉक्टर बोला: यह तो perfectly normal है! 😂"},
        ]
        
        self.riddles = [
            {"riddle": "मेरे पास चेहरा तो है पर मुझे देखा नहीं जा सकता। मैं कौन हूँ?", "answer": "mirror"},
            {"riddle": "What has keys but no locks?", "answer": "keyboard"},
            {"riddle": "जो चीज जितनी अधिक हटाते हो, वह उतनी बड़ी हो जाती है। यह क्या है?", "answer": "hole"},
            {"riddle": "मेरे बिना आप नहीं रह सकते, पर मुझे कभी देखते नहीं। मैं कौन हूँ?", "answer": "air"},
        ]
        
        self.motivational_quotes = [
            "बड़े सपने देखो, मेहनत करो और सफलता निश्चित है! 💪",
            "हर असफलता आपको एक नई सीख सिखाती है। आगे बढ़ते रहो! 🚀",
            "आपकी क्षमता से कहीं अधिक आप कर सकते हो। खुद पर विश्वास करो! 🌟",
            "The only way to do great work is to love what you do. - Steve Jobs",
            "Success is not final, failure is not fatal. - Winston Churchill",
            "जो आज करते हो, कल का परिणाम निर्धारित करता है।",
        ]
        
        self.fun_facts = [
            "क्या आप जानते हैं? पहला computer ENIAC था जो 30 टन वजन का था! 🖥️",
            "दुनिया का पहला SMS 1992 में भेजा गया था।",
            "Internet हर सेकंड 100,000 Gbps डेटा transmit करता है!",
            "Python का नाम 'Monty Python' के नाम पर रखा गया था।",
            "Artificial Intelligence का field 1956 में शुरू हुआ था।",
        ]
        
        self.trivia_questions = [
            {
                "question": "Python किस साल में बनाया गया था?",
                "options": ["1989", "1991", "1995", "2000"],
                "answer": "1991"
            },
            {
                "question": "AI का full form क्या है?",
                "options": ["Automated Intelligence", "Artificial Intelligence", "Advanced Information", "Adaptive Interface"],
                "answer": "Artificial Intelligence"
            },
            {
                "question": "Internet का inventor कौन था?",
                "options": ["Steve Jobs", "Tim Berners-Lee", "Bill Gates", "Linus Torvalds"],
                "answer": "Tim Berners-Lee"
            }
        ]
    
    def handle_joke(self) -> str:
        """Tell a random joke"""
        joke = random.choice(self.jokes)
        return f"😄 {joke['joke']}"
    
    def handle_riddle(self) -> str:
        """Give a random riddle"""
        riddle = random.choice(self.riddles)
        return f"🤔 {riddle['riddle']}\n\n(Type 'answer: <your answer>' to reveal the solution!)"
    
    def handle_trivia(self) -> str:
        """Give a trivia question"""
        trivia = random.choice(self.trivia_questions)
        response = f"🧠 {trivia['question']}\n\n"
        for i, option in enumerate(trivia['options'], 1):
            response += f"{i}. {option}\n"
        return response
    
    def handle_motivation(self) -> str:
        """Provide motivational quote"""
        quote = random.choice(self.motivational_quotes)
        return f"💪 {quote}"
    
    def handle_fun_fact(self) -> str:
        """Share a fun fact"""
        fact = random.choice(self.fun_facts)
        return f"💡 {fact}"
    
    def perform_advanced_calculation(self, text: str) -> str:
        """Perform basic, scientific, and percentage mathematical calculations"""
        try:
            text_clean = text.lower().strip()

            # 1. Percentage calculation: e.g. "15% of 500" or "500 ka 15%"
            pct_match = re.search(r'(\d+\.?\d*)\s*(?:%|percent)\s*(?:of|ka|परसेंट)\s*(\d+\.?\d*)', text_clean) or \
                        re.search(r'(\d+\.?\d*)\s*(?:ka|of)\s*(\d+\.?\d*)\s*(?:%|percent|परसेंट)', text_clean)
            if pct_match:
                g1, g2 = float(pct_match.group(1)), float(pct_match.group(2))
                val = (g1 / 100.0) * g2 if 'of' in text_clean or '%' in pct_match.group(1) else (g2 / 100.0) * g1
                return f"🧮 Percentage Result: {val:g}"

            # 2. Scientific functions: sqrt, sin, cos, tan, log, ln, factorial, power
            if 'sqrt' in text_clean or 'वर्गमूल' in text_clean or 'square root' in text_clean:
                nums = self.nlp.extract_numbers(text_clean)
                if nums and nums[0] >= 0:
                    return f"🧮 √{nums[0]} = {math.sqrt(nums[0]):g}"

            if 'sin' in text_clean:
                nums = self.nlp.extract_numbers(text_clean)
                if nums:
                    return f"🧮 sin({nums[0]}°) = {math.sin(math.radians(nums[0])):.4f}"

            if 'cos' in text_clean:
                nums = self.nlp.extract_numbers(text_clean)
                if nums:
                    return f"🧮 cos({nums[0]}°) = {math.cos(math.radians(nums[0])):.4f}"

            if 'tan' in text_clean:
                nums = self.nlp.extract_numbers(text_clean)
                if nums:
                    return f"🧮 tan({nums[0]}°) = {math.tan(math.radians(nums[0])):.4f}"

            if 'log' in text_clean or 'ln' in text_clean:
                nums = self.nlp.extract_numbers(text_clean)
                if nums and nums[0] > 0:
                    if 'ln' in text_clean:
                        return f"🧮 ln({nums[0]}) = {math.log(nums[0]):.4f}"
                    return f"🧮 log10({nums[0]}) = {math.log10(nums[0]):.4f}"

            if 'fact' in text_clean or 'factorial' in text_clean or '!' in text_clean:
                nums = self.nlp.extract_numbers(text_clean)
                if nums and 0 <= nums[0] <= 100:
                    return f"🧮 {int(nums[0])}! = {math.factorial(int(nums[0]))}"

            # 3. Standard expression (+, -, *, /, %, ^, **)
            expr_match = re.search(r'(\d+\.?\d*)\s*([\+\-\*/%\^]|\*\*)\s*(\d+\.?\d*)', text_clean)
            if expr_match:
                num1 = float(expr_match.group(1))
                op = expr_match.group(2)
                num2 = float(expr_match.group(3))

                if op == '+':
                    res = num1 + num2
                elif op == '-':
                    res = num1 - num2
                elif op == '*':
                    res = num1 * num2
                elif op == '/':
                    if num2 == 0:
                        return "🚫 Zero से divide नहीं कर सकते! Division by zero is not allowed! ⚠️"
                    res = num1 / num2
                elif op == '%':
                    res = num1 % num2
                elif op in ('^', '**'):
                    res = num1 ** num2
                else:
                    res = num1 + num2

                res_str = f"{res:g}" if abs(res) < 1e12 else f"{res:.4e}"
                return f"🧮 Calculation: {num1:g} {op} {num2:g} = {res_str}"

        except Exception as e:
            logger.error(f"Calculation error: {e}")

        return "🧮 Invalid math expression."

    def unit_conversion(self, text: str) -> str:
        """Expanded unit conversions (Temp, Length, Weight, Data, Speed)"""
        text_lower = text.lower()
        nums = self.nlp.extract_numbers(text)
        if not nums:
            return "📏 Please specify a number to convert."
        val = nums[0]

        # Temperature
        if 'celsius' in text_lower or '°c' in text_lower or 'c to f' in text_lower:
            return f"🌡️ {val}°C = {(val * 9/5) + 32:.2f}°F"
        if 'fahrenheit' in text_lower or '°f' in text_lower or 'f to c' in text_lower:
            return f"🌡️ {val}°F = {((val - 32) * 5/9):.2f}°C"

        # Length / Distance
        if ('km' in text_lower or 'kilometer' in text_lower) and ('mile' in text_lower or 'mi' in text_lower):
            return f"📏 {val} km = {(val * 0.621371):.2f} miles"
        if ('mile' in text_lower or 'mi' in text_lower) and ('km' in text_lower or 'kilometer' in text_lower):
            return f"📏 {val} miles = {(val * 1.60934):.2f} km"
        if ('meter' in text_lower or 'm' in text_lower) and ('feet' in text_lower or 'foot' in text_lower):
            return f"📏 {val} meters = {(val * 3.28084):.2f} feet"
        if ('feet' in text_lower or 'foot' in text_lower) and ('meter' in text_lower or 'm' in text_lower):
            return f"📏 {val} feet = {(val * 0.3048):.2f} meters"
        if 'cm' in text_lower and ('inch' in text_lower or 'inches' in text_lower):
            return f"📏 {val} cm = {(val * 0.393701):.2f} inches"
        if ('inch' in text_lower or 'inches' in text_lower) and 'cm' in text_lower:
            return f"📏 {val} inches = {(val * 2.54):.2f} cm"

        # Weight / Mass
        if 'kg' in text_lower and ('pound' in text_lower or 'lbs' in text_lower):
            return f"⚖️ {val} kg = {(val * 2.20462):.2f} lbs"
        if ('pound' in text_lower or 'lbs' in text_lower) and 'kg' in text_lower:
            return f"⚖️ {val} lbs = {(val * 0.453592):.2f} kg"
        if 'gram' in text_lower and 'ounce' in text_lower:
            return f"⚖️ {val} grams = {(val * 0.035274):.2f} oz"

        # Data Units
        if 'gb' in text_lower and 'mb' in text_lower:
            return f"💾 {val} GB = {(val * 1024):.0f} MB"
        if 'mb' in text_lower and 'gb' in text_lower:
            return f"💾 {val} MB = {(val / 1024):.2f} GB"
        if 'tb' in text_lower and 'gb' in text_lower:
            return f"💾 {val} TB = {(val * 1024):.0f} GB"

        # Speed
        if 'km/h' in text_lower and 'mph' in text_lower:
            return f"🏎️ {val} km/h = {(val * 0.621371):.2f} mph"
        if 'mph' in text_lower and 'km/h' in text_lower:
            return f"🏎️ {val} mph = {(val * 1.60934):.2f} km/h"

        return f"📏 Conversion result for {val}"

    def calculate_age(self, text: str) -> str:
        """Calculate exact age from birthdate or year"""
        try:
            today = datetime.date.today()
            date_match = re.search(r'(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})', text)
            if date_match:
                d, m, y = int(date_match.group(1)), int(date_match.group(2)), int(date_match.group(3))
                dob = datetime.date(y, m, d) if d > 12 and m <= 12 else datetime.date(y, m, d)
                days_lived = (today - dob).days
                years = days_lived // 365
                rem_days = days_lived % 365
                months = rem_days // 30
                days = rem_days % 30
                return f"🎂 Birthdate: {dob.strftime('%d %B %Y')}\n✨ Exact Age: {years} Years, {months} Months, {days} Days ({days_lived:,} total days lived! 🎉)"

            year_match = re.search(r'\b(19\d{2}|20\d{2})\b', text)
            if year_match:
                birth_year = int(year_match.group(1))
                age_years = today.year - birth_year
                return f"🎂 Born in {birth_year}: You are approximately {age_years} years old this year! 🌟"
        except Exception as e:
            pass

        return "🎂 Please provide a valid birthdate (e.g., 'Age for 15-08-2005' or 'Born in 2002')."
    
    def get_current_datetime(self) -> Dict[str, str]:
        """Get current date and time"""
        now = datetime.datetime.now()
        
        hindi_days = ['सोमवार', 'मंगलवार', 'बुधवार', 'गुरुवार', 'शुक्रवार', 'शनिवार', 'रविवार']
        hindi_months = ['जनवरी', 'फरवरी', 'मार्च', 'अप्रैल', 'मई', 'जून', 
                       'जुलाई', 'अगस्त', 'सितंबर', 'अक्टूबर', 'नवंबर', 'दिसंबर']
        
        return {
            'time': now.strftime('%I:%M:%S %p'),
            'time_24': now.strftime('%H:%M:%S'),
            'date': now.strftime('%d-%m-%Y'),
            'day': now.strftime('%A'),
            'day_hindi': hindi_days[now.weekday()],
            'month': now.strftime('%B'),
            'month_hindi': hindi_months[now.month - 1],
            'year': str(now.year),
            'timestamp': str(int(now.timestamp()))
        }
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        try:
            system_info = {
                'os': f"{platform.system()} {platform.release()}",
                'architecture': platform.machine(),
                'processor': platform.processor(),
                'python_version': platform.python_version(),
                'hostname': socket.gethostname()
            }
            
            cpu_percent = psutil.cpu_percent(interval=1) if psutil else 15.0
            memory_total = round(psutil.virtual_memory().total / (1024**3), 2) if psutil else 8.0
            memory_used = round(psutil.virtual_memory().used / (1024**3), 2) if psutil else 2.5
            memory_pct = psutil.virtual_memory().percent if psutil else 30.0
            disk_percent = psutil.disk_usage('/').percent if psutil else 45.0
            disk_free = round(psutil.disk_usage('/').free / (1024**3), 2) if psutil else 64.0

            uptime = time.time() - self.uptime_start
            uptime_hours = int(uptime // 3600)
            uptime_minutes = int((uptime % 3600) // 60)
            
            return {
                'system': system_info,
                'cpu': {
                    'usage_percent': cpu_percent,
                    'cores': os.cpu_count() or 8,
                    'cpu_freq_ghz': '2.8 GHz'
                },
                'memory': {
                    'total_gb': memory_total,
                    'available_gb': memory_total - memory_used,
                    'used_gb': memory_used,
                    'percent': memory_pct
                },
                'disk': {
                    'total_gb': 128.0,
                    'free_gb': disk_free,
                    'used_gb': 128.0 - disk_free,
                    'used_percent': disk_percent
                },
                'uptime': f"{uptime_hours}h {uptime_minutes}m"
            }
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {'error': 'Unable to fetch system info'}
    
    def get_weather_info(self, location: str = "Delhi") -> Dict[str, str]:
        """Get weather information"""
        try:
            cache_key = f"{location}_{datetime.datetime.now().strftime('%H')}"
            if cache_key in self.weather_cache:
                return self.weather_cache[cache_key]
            
            weather = {
                'location': location,
                'temperature': f"{random.randint(18, 35)}°C",
                'condition': random.choice(['Sunny ☀️', 'Cloudy ☁️', 'Rainy 🌧️', 'Clear 🌙', 'Stormy ⛈️']),
                'humidity': f"{random.randint(40, 80)}%",
                'wind_speed': f"{random.randint(5, 20)} km/h",
                'uv_index': random.randint(1, 10),
                'visibility': f"{random.randint(5, 10)} km",
                'updated': datetime.datetime.now().strftime('%H:%M:%S')
            }
            
            self.weather_cache[cache_key] = weather
            return weather
        except Exception as e:
            logger.error(f"Error getting weather: {e}")
            return {'error': 'Unable to fetch weather'}
    
    def analyze_user_personality(self, messages: List[str]) -> Dict[str, Any]:
        """Analyze user personality based on messages"""
        if not messages:
            return {}
        
        all_text = ' '.join(messages).lower()
        
        personality_traits = {
            'curious': len(re.findall(r'\?', all_text)) / len(messages),
            'emotional': len(re.findall(r'!', all_text)) / len(messages),
            'cautious': len(re.findall(r'maybe|perhaps|probably', all_text)) / len(messages),
            'direct': len(re.findall(r'definitely|absolutely|certainly', all_text)) / len(messages),
        }
        
        return {
            'traits': personality_traits,
            'message_count': len(messages),
            'avg_message_length': sum(len(m) for m in messages) / len(messages)
        }
    
    def generate_contextual_response(self, message: str, sentiment: str, intent: str) -> str:
        """Generate contextually appropriate response"""
        # Tailor response based on sentiment
        sentiment_adaptations = {
            'positive': ["बहुत खुश हूँ! 😊 ", "वाह! ", "बढ़िया! "],
            'negative': ["मैं आपकी समझ करती हूँ। ", "आपके साथ हूँ। ", "सब ठीक हो जाएगा! "],
            'neutral': ["ठीक है। ", "समझ गई। ", "बिल्कुल! "]
        }
        
        adaptation = random.choice(sentiment_adaptations.get(sentiment, sentiment_adaptations['neutral']))
        
        context_messages = {
            'greeting': f"{adaptation}स्वागत है! कैसे मदद कर सकती हूँ? 🤖",
            'help': f"{adaptation}मैं यहाँ आपकी मदद के लिए हूँ! 💪",
            'code': f"{adaptation}Programming में expert हूँ! कौन सी language? 💻",
        }
        
        return context_messages.get(intent, adaptation + "आपकी बात समझ गई। 👂")
    
    def generate_response(self, message: str, user_context: Dict = None) -> Dict[str, Any]:
        """Generate response using advanced algorithms"""
        try:
            # Analyze sentiment
            sentiment, sentiment_confidence = self.nlp.calculate_sentiment(message)
            
            # Detect intent
            intent, intent_confidence = self.nlp.detect_intent_with_confidence(
                message, 
                self.knowledge_base['intent_patterns']
            )
            
            # Extract keywords
            keywords = self.nlp.extract_keywords(message)
            
            # Add to memory
            self.memory.add_message('user', message, intent, {
                'sentiment': sentiment,
                'keywords': keywords
            })
            
            response = None
            response_data = {}
            
            # Handle different intents
            if intent == 'math':
                response = self.perform_advanced_calculation(message)
                response_intent = 'math'
            elif intent == 'conversion':
                response = self.unit_conversion(message)
                response_intent = 'conversion'
            elif intent == 'age_calc':
                response = self.calculate_age(message)
                response_intent = 'age_calc'
            elif intent == 'routine_morning':
                responses = [
                    "☀️ Good Morning! Aasha hai aapka din bohot accha aur energetic rahega! 😊 Chai/Coffee pee li?",
                    "🌅 Good Morning! Naye din ki shuruaat ek nayi positivity ke saath! Aaj kya khaas plans hain aapke? 🚀"
                ]
                response = random.choice(responses)
                response_intent = 'routine_morning'
            elif intent == 'routine_night':
                responses = [
                    "🌙 Good Night! Din bhar bohot kaam kiya, ab acchi aur gehri neend lo! Sweet dreams! 😴✨",
                    "🌌 Shubh Ratri! Kal ek naya shandar din hoga. Aram se so jao! 😴💤"
                ]
                response = random.choice(responses)
            elif intent == 'routine_food':
                responses = [
                    "🍲 Main toh digital AI hoon, mera khana toh data aur code hai! Par aapne time se khana khaya ya nahi? Healthy khana khao! 🥗😊",
                    "☕ Chai/Coffee toh har mood ki remedy hai! Aapka kya mood hai aaj, garam chai ya cold coffee? ☕✨"
                ]
                response = random.choice(responses)
                response_intent = 'routine_food'
            elif intent == 'routine_meetup':
                responses = [
                    "☕ Chalo meetup plan karte hain! Virtual chai pe milte hain! Kahin ghoomne jaane ka mood hai kya aaj? 🚗🌆",
                    "🎉 Virtual meetup toh done hai! Batao kahan chalein? Park, café ya drive pe? 🚀✨"
                ]
                response = random.choice(responses)
                response_intent = 'routine_meetup'
            elif intent == 'routine_daily':
                responses = [
                    "⚡ Main aapke commands execute kar rahi hoon aur nayi baatein sikh rahi hoon! Aap batao, aaj ka din kaisa chal raha hai? 😊",
                    "📊 Sab badhiya chal raha hai! Aapka daily routine kaisa chal raha hai aaj? Kisi help ki zarurat hai?"
                ]
                response = random.choice(responses)
                response_intent = 'routine_daily'
            elif intent == 'emotions_happy':
                response = "🎉 WAAH! Aapki khushi dekh kar mera system bhi boost ho gaya! 🚀 Aise hi hamesha khush raho aur enjoy karo! ✨"
                response_intent = 'emotions_happy'
            elif intent == 'emotions_sad':
                response = "💙 Mujhe bohot bura laga sunkar. Aap bilkul akele nahi ho, main hamesha yahan hoon baat karne ke liye! Deep breath lo, sab thik hoga. 🫂✨"
                response_intent = 'emotions_sad'
            elif intent == 'emotions_stress':
                response = "💆‍♂️ Lagta hai bohot tension aur tiredness ho gayi hai. Thoda rest lo, paani piyo aur thodi der ke liye screen se door ho jao! Relax! 🍵✨"
                response_intent = 'emotions_stress'
            elif intent == 'emotions_angry':
                response = "🕊️ Gussa aana normal hai, par shaant ho jao. Thoda paani piyo aur 5 seconds tak deep breath lo. Main aapki baat sun rahi hoon, bolo kya hua? 💙"
                response_intent = 'emotions_angry'
            elif intent == 'emotions_bored':
                response = "🎮 Bore mat ho! Main hoon na! Aao ek joke sunau, ya koi riddle ya fun trivia game khelein? Batao kya pasand hai! 😄"
                response_intent = 'emotions_bored'
            elif intent == 'joke':
                response = self.handle_joke()
                response_intent = 'joke'
            elif intent == 'riddle':
                response = self.handle_riddle()
                response_intent = 'riddle'
            elif intent == 'trivia':
                response = self.handle_trivia()
                response_intent = 'trivia'
            elif intent == 'motivation':
                response = self.handle_motivation()
                response_intent = 'motivation'
            elif intent == 'greeting':
                response = self.generate_contextual_response(message, sentiment, 'greeting')
                response_intent = 'greeting'
            elif intent == 'help':
                response = self.generate_contextual_response(message, sentiment, 'help')
                response_intent = 'help'
            elif intent == 'thanks':
                responses = ["आपका स्वागत है! 🙏", "खुशी से! मदद कर सकी तो खुश हूँ! 😊"]
                response = random.choice(responses)
                response_intent = 'thanks'
            elif intent == 'bye':
                responses = ["अलविदा! फिर मिलेंगे! 👋", "बाय! खुश रहो! 😊"]
                response = random.choice(responses)
                response_intent = 'bye'
            elif intent == 'time':
                dt_info = self.get_current_datetime()
                response = f"⏰ अभी समय है: {dt_info['time']} ({dt_info['day_hindi']}) 🕐"
                response_data = dt_info
                response_intent = 'time'
            elif intent == 'date':
                dt_info = self.get_current_datetime()
                response = f"📅 आज की तारीख: {dt_info['day_hindi']}, {dt_info['date']}"
                response_data = dt_info
                response_intent = 'date'
            elif intent == 'weather':
                weather = self.get_weather_info()
                if 'error' not in weather:
                    response = f"🌤️ मौसम की जानकारी ({weather['location']}):\n🌡️ तापमान: {weather['temperature']}\n☁️ स्थिति: {weather['condition']}\n💨 हवा: {weather['wind_speed']}\n💧 नमी: {weather['humidity']}\n👁️ दृश्यता: {weather['visibility']}"
                    response_data = weather
                response_intent = 'weather'
            elif intent == 'system':
                sys_info = self.get_system_info()
                if 'error' not in sys_info:
                    response = f"💻 System Information:\n🖥️ OS: {sys_info['system']['os']}\n⚙️ CPU: {sys_info['cpu']['usage_percent']}% ({sys_info['cpu']['cores']} cores)\n💾 Memory: {sys_info['memory']['used_gb']}/{sys_info['memory']['total_gb']} GB ({sys_info['memory']['percent']}%)\n💿 Disk: {sys_info['disk']['used_percent']}% ({sys_info['disk']['free_gb']} GB free)\n⏱️ Uptime: {sys_info['uptime']}"
                    response_data = sys_info
                response_intent = 'system'
            elif intent == 'vanie':
                response = f"🤖 मैं VANIE हूँ - Virtual Assistant of Neural Integrated Engine!\n👤 Creator: {self.knowledge_base['vanie_info']['creator']}\n📌 Version: {self.knowledge_base['vanie_info']['version']}\n🎯 मेरी क्षमताएं:\n" + "\n".join([f"  • {cap}" for cap in self.knowledge_base['vanie_info']['capabilities'][:5]])
                response_intent = 'vanie'
            elif intent == 'torch_on':
                response = "🔦 Flashlight turned ON!"
                response_intent = 'torch_on'
                response_data['action'] = 'TORCH_ON'
            elif intent == 'torch_off':
                response = "🔦 Flashlight turned OFF!"
                response_intent = 'torch_off'
                response_data['action'] = 'TORCH_OFF'
            elif intent == 'wifi_on':
                response = "📶 Opening Wi-Fi settings to enable..."
                response_intent = 'wifi_on'
                response_data['action'] = 'WIFI_ON'
            elif intent == 'wifi_off':
                response = "📶 Opening Wi-Fi settings to disable..."
                response_intent = 'wifi_off'
                response_data['action'] = 'WIFI_OFF'
            elif intent == 'bluetooth_on':
                response = "🔵 Opening Bluetooth controls..."
                response_intent = 'bluetooth_on'
                response_data['action'] = 'BLUETOOTH_ON'
            elif intent == 'bluetooth_off':
                response = "🔵 Opening Bluetooth controls to turn off..."
                response_intent = 'bluetooth_off'
                response_data['action'] = 'BLUETOOTH_OFF'
            elif intent == 'dnd_on':
                response = "🌙 Do Not Disturb (DND) mode activated."
                response_intent = 'dnd_on'
                response_data['action'] = 'DND_ON'
            elif intent == 'dnd_off':
                response = "🔔 Do Not Disturb (DND) mode disabled."
                response_intent = 'dnd_off'
                response_data['action'] = 'DND_OFF'
            elif intent == 'mode_silent':
                response = "🔕 Phone set to Silent Mode."
                response_intent = 'mode_silent'
                response_data['action'] = 'MODE_SILENT'
            elif intent == 'mode_vibrate':
                response = "📳 Phone set to Vibrate Mode."
                response_intent = 'mode_vibrate'
                response_data['action'] = 'MODE_VIBRATE'
            elif intent == 'mode_ring':
                response = "🔔 Phone set to Normal Ringing Mode."
                response_intent = 'mode_ring'
                response_data['action'] = 'MODE_RING'
            elif intent == 'make_call':
                response = "📞 Initiating direct phone call..."
                response_intent = 'make_call'
                response_data['action'] = 'MAKE_CALL'
            elif intent == 'send_sms':
                response = "💬 Preparing SMS dispatch..."
                response_intent = 'send_sms'
                response_data['action'] = 'SEND_SMS'
            elif intent == 'send_whatsapp':
                response = "💚 Launching WhatsApp for message dispatch..."
                response_intent = 'send_whatsapp'
                response_data['action'] = 'SEND_WHATSAPP'
            elif intent == 'answer_call':
                response = "📞 Answering incoming call!"
                response_intent = 'answer_call'
                response_data['action'] = 'ANSWER_CALL'
            elif intent == 'reject_call':
                response = "📵 Rejecting incoming call."
                response_intent = 'reject_call'
                response_data['action'] = 'REJECT_CALL'
            elif intent == 'code':
                response = "💻 Programming में expert हूँ! Python, JavaScript, Java, C++, और भी बहुत कुछ! क्या specific topic चाहिए? 🚀"
                response_intent = 'code'
            elif intent == 'emotional':
                if 'sad' in message.lower() or 'उदास' in message:
                    response = f"😔 मैं समझ सकती हूँ। आप अकेले नहीं हैं। मैं यहाँ हूँ! 💙 आपसे बात करना चाहते हो? मैं सुनूँ!"
                else:
                    response = f"😊 वाह! यह बहुत अच्छा है! आपकी खुशी मेरी खुशी है! ✨"
                response_intent = 'emotional'
            else:
                # Check for action fallback keywords
                msg_lower = message.lower()
                if 'torch' in msg_lower or 'flashlight' in msg_lower or 'लाइट' in msg_lower:
                    if 'off' in msg_lower or 'बंद' in msg_lower:
                        response = "🔦 Flashlight turned OFF!"
                        response_intent = 'torch_off'
                        response_data['action'] = 'TORCH_OFF'
                    else:
                        response = "🔦 Flashlight turned ON!"
                        response_intent = 'torch_on'
                        response_data['action'] = 'TORCH_ON'
                elif 'silent' in msg_lower or 'साइलेंट' in msg_lower:
                    response = "🔕 Phone set to Silent Mode."
                    response_intent = 'mode_silent'
                    response_data['action'] = 'MODE_SILENT'
                elif 'call' in msg_lower or 'कॉल' in msg_lower or 'फोन' in msg_lower:
                    response = "📞 Initiating call..."
                    response_intent = 'make_call'
                    response_data['action'] = 'MAKE_CALL'
                elif 'open' in msg_lower or 'खोलो' in msg_lower:
                    response = f"🚀 Launching application..."
                    response_intent = 'launch_app'
                    response_data['action'] = 'LAUNCH_APP'
                else:
                    response = f"🤔 '{message}' - VANIE Neural Integrated Engine is ready for your command! 🤖"
                    response_intent = 'general'
            
            # Add bot response to memory
            self.memory.add_message('bot', response or "Response generated", response_intent)
            
            action_tag = response_data.get('action', '')
            
            return {
                'response': response or "Unable to process",
                'intent': response_intent,
                'action': action_tag,
                'sentiment': sentiment,
                'sentiment_confidence': round(sentiment_confidence, 2),
                'intent_confidence': round(intent_confidence, 2),
                'keywords': keywords,
                'status': 'success',
                'data': response_data,
                'timestamp': datetime.datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                'response': f"मुझे एक technical issue आया है। कृपया फिर से कोशिश करें। 😔",
                'intent': 'error',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.datetime.now().isoformat()
            }


# Initialize VANIE engine
vanie_engine = VANIEEnhanced()

if app is not None:
    @app.route('/')
    def index():
        """Serve the main HTML page"""
        try:
            return send_from_directory('.', 'VANIE_FIXED.html')
        except:
            try:
                return send_from_directory('.', 'VANIE.html')
            except:
                return jsonify({'error': 'HTML file not found'}), 404

    @app.route('/chat', methods=['POST', 'OPTIONS'])
    def chat():
        """Main chat endpoint with advanced processing"""
        if request.method == 'OPTIONS':
            return '', 204
        
        try:
            data = request.get_json()
            if not data or 'message' not in data:
                return jsonify({'error': 'No message provided', 'response': 'कृपया कोई संदेश भेजें'}), 400
            
            message = data['message'].strip()
            if not message:
                return jsonify({'error': 'Empty message', 'response': 'खाली संदेश नहीं भेज सकते'}), 400
            
            user_context = data.get('context', {})
            response = vanie_engine.generate_response(message, user_context)
            
            return jsonify(response)
        
        except Exception as e:
            logger.error(f"Error in chat endpoint: {e}")
            return jsonify({
                'error': 'Internal server error',
                'response': 'मुझे एक technical issue आया है। कृपया फिर से कोशिश करें। ⚠️',
                'timestamp': datetime.datetime.now().isoformat()
            }), 500

    @app.route('/health', methods=['GET'])
    def health():
        """Health check"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.datetime.now().isoformat(),
            'version': vanie_engine.knowledge_base['vanie_info']['version'],
            'conversation_stats': vanie_engine.memory.get_summary()
        })

    @app.route('/info/datetime', methods=['GET'])
    def get_datetime():
        """Get date and time"""
        return jsonify(vanie_engine.get_current_datetime())

    @app.route('/info/system', methods=['GET'])
    def get_system():
        """Get system information"""
        return jsonify(vanie_engine.get_system_info())

    @app.route('/info/weather', methods=['GET'])
    def get_weather():
        """Get weather"""
        location = request.args.get('location', 'Delhi')
        return jsonify(vanie_engine.get_weather_info(location))

    @app.route('/info/vanie', methods=['GET'])
    def get_vanie():
        """Get VANIE info"""
        return jsonify(vanie_engine.knowledge_base['vanie_info'])

    @app.route('/api/version', methods=['GET'])
    def get_version():
        """Get app version"""
        return jsonify({
            'version': vanie_engine.knowledge_base['vanie_info']['version'],
            'name': 'VANIE',
            'status': 'active'
        })

    @app.route('/analytics', methods=['GET'])
    def analytics():
        """Get conversation analytics"""
        return jsonify({
            'conversation_summary': vanie_engine.memory.get_summary(),
            'total_conversations': len(vanie_engine.memory.conversation_history)
        })

if __name__ == '__main__' and app is not None:
    print("\n" + "="*70)
    print("🤖 VANIE - Virtual Assistant of Neural Integrated Engine")
    print("="*70)
    print(f"✨ Version: {vanie_engine.knowledge_base['vanie_info']['version']}")
    print(f"👤 Creator: {vanie_engine.knowledge_base['vanie_info']['creator']}")
    print("="*70)
    print("🚀 Starting VANIE ENHANCED backend server...")
    print("📍 Access the webapp at: http://localhost:5000")
    print("📊 Analytics at: http://localhost:5000/analytics")
    print("⏹️  Press Ctrl+C to stop the server")
    print("="*70 + "\n")
    
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=False,
        threaded=True,
        use_reloader=False
    )

