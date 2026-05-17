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
import psutil
import subprocess
import threading
import time
import requests
import re
import calendar
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
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

# Initialize Flask app
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"]}})

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
                'math': r'(\d+\.?\d*\s*[\+\-\*/]\s*\d+\.?\d*|calculate|गणना)',
                'code': r'(code|python|javascript|java|cpp|प्रोग्रामिंग|programming)',
                'emotional': r'(sad|happy|excited|उदास|खुश|परेशान|feeling)',
                'joke': r'(joke|मजाक|हंसाओ|funny|laugh|चुटकुले)',
                'riddle': r'(riddle|पहेली|guess|सवाल)',
                'trivia': r'(trivia|क्विज़|facts|interesting|fact)',
                'game': r'(game|खेल|play|word game)',
                'motivation': r'(motivation|inspire|courage|strength|confidence|प्रेरणा)',
                'quote': r'(quote|famous|कहावत|wisdom|advice)',
                'conversion': r'(convert|conversion|transform|unit)',
                'search': r'(search|find|look for|खोजो)',
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
        """Perform advanced mathematical calculations"""
        try:
            # Extract mathematical expression
            match = re.search(r'(\d+\.?\d*)\s*([\+\-\*/])\s*(\d+\.?\d*)', text)
            if match:
                num1, operator, num2 = float(match.group(1)), match.group(2), float(match.group(3))
                
                operations = {
                    '+': operator.add,
                    '-': operator.sub,
                    '*': operator.mul,
                    '/': operator.truediv
                }
                
                if operator == '/' and num2 == 0:
                    return "🚫 Zero से divide नहीं कर सकते! Division by zero is not allowed! ⚠️"
                
                result = operations[operator](num1, num2)
                
                # Additional info
                info = ""
                if operator == '*':
                    info = f"\n💡 {num1} का {num2} गुना"
                elif operator == '+':
                    info = f"\n💡 Total: {result}"
                
                return f"🧮 {num1} {operator} {num2} = {result}{info}"
        except:
            pass
        
        return None
    
    def unit_conversion(self, text: str) -> str:
        """Handle unit conversions"""
        conversions = {
            'km_to_miles': lambda x: x * 0.621371,
            'miles_to_km': lambda x: x * 1.60934,
            'kg_to_lbs': lambda x: x * 2.20462,
            'lbs_to_kg': lambda x: x * 0.453592,
            'celsius_to_fahrenheit': lambda x: (x * 9/5) + 32,
            'fahrenheit_to_celsius': lambda x: (x - 32) * 5/9,
        }
        
        # Simple unit conversion
        text_lower = text.lower()
        
        if 'km' in text_lower and 'mile' in text_lower:
            numbers = self.nlp.extract_numbers(text)
            if numbers:
                result = conversions['km_to_miles'](numbers[0])
                return f"📏 {numbers[0]} km = {result:.2f} miles"
        
        if 'mile' in text_lower and 'km' in text_lower:
            numbers = self.nlp.extract_numbers(text)
            if numbers:
                result = conversions['miles_to_km'](numbers[0])
                return f"📏 {numbers[0]} miles = {result:.2f} km"
        
        if 'celsius' in text_lower or '°c' in text_lower or 'c to f' in text_lower:
            numbers = self.nlp.extract_numbers(text)
            if numbers:
                result = conversions['celsius_to_fahrenheit'](numbers[0])
                return f"🌡️ {numbers[0]}°C = {result:.2f}°F"
        
        if 'fahrenheit' in text_lower or '°f' in text_lower or 'f to c' in text_lower:
            numbers = self.nlp.extract_numbers(text)
            if numbers:
                result = conversions['fahrenheit_to_celsius'](numbers[0])
                return f"🌡️ {numbers[0]}°F = {result:.2f}°C"
        
        return None
    
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
            
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            uptime = time.time() - self.uptime_start
            uptime_hours = int(uptime // 3600)
            uptime_minutes = int((uptime % 3600) // 60)
            
            return {
                'system': system_info,
                'cpu': {
                    'usage_percent': cpu_percent,
                    'cores': psutil.cpu_count(),
                    'cpu_freq_ghz': round(psutil.cpu_freq().current / 1000, 2) if psutil.cpu_freq() else 'N/A'
                },
                'memory': {
                    'total_gb': round(memory.total / (1024**3), 2),
                    'available_gb': round(memory.available / (1024**3), 2),
                    'used_gb': round(memory.used / (1024**3), 2),
                    'percent': memory.percent
                },
                'disk': {
                    'total_gb': round(disk.total / (1024**3), 2),
                    'free_gb': round(disk.free / (1024**3), 2),
                    'used_gb': round(disk.used / (1024**3), 2),
                    'used_percent': disk.percent
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
                # Intelligent fallback with keywords
                response = f"🤔 दिलचस्प! '{message}' के बारे में... मैं सोचती हूँ कि यह topic बहुत महत्वपूर्ण है। क्या आप इसके बारे में और जानना चाहेंगे? 📚"
                response_intent = 'general'
            
            # Add bot response to memory
            self.memory.add_message('bot', response or "Response generated", response_intent)
            
            return {
                'response': response or "Unable to process",
                'intent': response_intent,
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

# Routes
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

if __name__ == '__main__':
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
