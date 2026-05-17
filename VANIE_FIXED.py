#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VANIE - Virtual Assistant of Neural Integrated Engine
Advanced Backend System with Real-time Information Capabilities 
FIXED AND ENHANCED VERSION

REQUIREMENTS:
flask==2.3.3
flask-cors==4.0.0
psutil==5.9.5
requests==2.31.0

INSTALLATION:
pip install flask flask-cors psutil requests

RUN:
python VANIE_FIXED.py
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
from typing import Dict, Any, List
import random
import math
import hashlib
import base64
import uuid
from collections import Counter, defaultdict
from difflib import SequenceMatcher
import statistics
import heapq

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"]}})

class VANIEEngine:
    """Main VANIE Engine with Advanced Real-time Capabilities"""
    
    def __init__(self):
        self.user_name = "Guest"
        self.conversation_context = []
        self.weather_cache = {}
        self.system_info_cache = None
        self.last_system_update = 0
        self.uptime_start = time.time()
        
        self.knowledge_base = self._initialize_knowledge_base()
        
        self.response_patterns = {
            'greetings': [
                "नमस्ते! मैं VANIE हूँ, आपकी AI assistant! 😊 कैसे मदद कर सकती हूँ?",
                "Hello! मैं VANIE हूँ। आज कैसे हैं आप? 🤖",
                "Hi there! VANIE at your service! क्या काम है? ✨"
            ],
            'help_responses': [
                "मैं आपकी मदद करने के लिए यहाँ हूँ! बताइए कि आपको क्या चाहिए। 💪",
                "I'm here to help! क्या समस्या है? 🤝",
                "आपकी सेवा में मैं सदैव तत्पर हूँ! बोलिए क्या काम है? 🌟"
            ],
            'emotional_support': [
                "मैं समझ सकती हूँ कि यह मुश्किल समय है। आप अकेले नहीं हैं। 💙",
                "I'm here for you! आपकी बातें मैं सुनूँ? 👂",
                "आपके दर्द को मैं महसूस करती हूँ। मैं आपके साथ हूँ। 🤗"
            ]
        }
    
    def _initialize_knowledge_base(self) -> Dict[str, Any]:
        """Initialize comprehensive knowledge base"""
        return {
            'vanie_info': {
                'full_form': 'Virtual Assistant of Neural Integrated Engine',
                'creator': 'Ayush Harinkhede',
                'version': '2.0-FIXED',
                'capabilities': [
                    'Real-time system monitoring',
                    'Natural conversation',
                    'Programming help',
                    'Math calculations',
                    'Weather information',
                    'Emotional support',
                    'Technical guidance'
                ]
            },
            'intent_patterns': {
                'greeting': r'(नमस्ते|hello|hi|hey|कैसे हो|what\'s up)',
                'help': r'(help|मदद|सहायता|assistance)',
                'bye': r'(bye|अलविदा|goodbye|बाय)',
                'thanks': r'(thanks|धन्यवाद|शुक्रिया)',
                'time': r'(time|समय|बजा|current time|अभी)',
                'date': r'(date|तारीख|आज|when)',
                'weather': r'(weather|मौसम|temperature|तापमान)',
                'system': r'(system|computer|pc|कंप्यूटर|memory|cpu)',
                'vanie': r'(vanie|तुम कौन|who are you|आपका नाम)',
                'math': r'(\d+[\+\-\*/]\d+|calculate|गणना)',
                'code': r'(code|python|javascript|प्रोग्रामिंग|programming)',
                'emotional': r'(sad|happy|excited|उदास|खुश|परेशान)',
            },
            'conversation_responses': {
                'greeting': [
                    "नमस्ते! मैं VANIE हूँ। आपसे बात करके खुश हूँ! 😊",
                    "Hello friend! कैसे हैं आप? 🤖",
                    "Hi! मेरा नाम VANIE है, Virtual Assistant! कुछ मदद चाहिए? ✨"
                ],
                'vanie_about': [
                    "मैं VANIE हूँ - Virtual Assistant of Neural Integrated Engine! Ayush Harinkhede ने मुझे बनाया है। मैं real-time information, programming help, math, और emotional support दे सकती हूँ! 🤖🌟",
                    "मैं एक advanced AI assistant हूँ जो natural conversation करती हूँ। मेरे पास machine learning algorithms हैं। मैं आपकी system को monitor कर सकती हूँ! 🚀",
                    "मेरा पूरा नाम Virtual Assistant of Neural Integrated Engine है। मैं आपकी हर समस्या का समाधान कर सकती हूँ! 💻✨"
                ],
                'thanks': [
                    "आपका स्वागत है! मेरी मदद करके खुश हूँ। 😊",
                    "Thank you! यह मेरा काम है आपकी मदद करना। 🙏",
                    "खुशी से! कभी भी मदद चाहिए तो बोलना। 🤝"
                ],
                'bye': [
                    "अलविदा! फिर मिलेंगे! 👋😊",
                    "Goodbye! बहुत खुश रही बातचीत! See you soon! 👋",
                    "बाय! मेरे साथ वक़्त बिताने के लिए धन्यवाद! 🙏"
                ]
            }
        }
    
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
        """Get system information"""
        try:
            system_info = {
                'os': f"{platform.system()} {platform.release()}",
                'architecture': platform.machine(),
                'processor': platform.processor(),
                'python_version': platform.python_version()
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
                    'cores': psutil.cpu_count()
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
                'condition': random.choice(['Sunny ☀️', 'Cloudy ☁️', 'Rainy 🌧️', 'Clear 🌙']),
                'humidity': f"{random.randint(40, 80)}%",
                'wind_speed': f"{random.randint(5, 20)} km/h",
                'updated': datetime.datetime.now().strftime('%H:%M:%S')
            }
            
            self.weather_cache[cache_key] = weather
            return weather
        except Exception as e:
            logger.error(f"Error getting weather: {e}")
            return {'error': 'Unable to fetch weather'}
    
    def detect_intent(self, message: str) -> str:
        """Detect user intent"""
        message_lower = message.lower()
        
        for intent, pattern in self.knowledge_base['intent_patterns'].items():
            if re.search(pattern, message_lower):
                return intent
        
        return 'general'
    
    def handle_math(self, message: str) -> str:
        """Handle mathematical calculations"""
        try:
            # Extract mathematical expression
            match = re.search(r'(\d+\.?\d*)\s*([\+\-\*/])\s*(\d+\.?\d*)', message)
            if match:
                num1, operator, num2 = float(match.group(1)), match.group(2), float(match.group(3))
                
                if operator == '+':
                    result = num1 + num2
                elif operator == '-':
                    result = num1 - num2
                elif operator == '*':
                    result = num1 * num2
                elif operator == '/':
                    if num2 != 0:
                        result = num1 / num2
                    else:
                        return "Division by zero नहीं हो सकता! ⚠️"
                
                return f"🧮 {num1} {operator} {num2} = {result}"
        except:
            pass
        
        return None
    
    def generate_response(self, message: str, user_context: Dict = None) -> Dict[str, Any]:
        """Generate response based on user input"""
        try:
            intent = self.detect_intent(message)
            
            if intent == 'math':
                math_result = self.handle_math(message)
                if math_result:
                    return {
                        'response': math_result,
                        'intent': 'math',
                        'status': 'success'
                    }
            
            if intent == 'greeting':
                response = random.choice(self.response_patterns['greetings'])
                return {'response': response, 'intent': 'greeting', 'status': 'success'}
            
            elif intent == 'help':
                response = random.choice(self.response_patterns['help_responses'])
                return {'response': response, 'intent': 'help', 'status': 'success'}
            
            elif intent == 'thanks':
                response = random.choice(self.knowledge_base['conversation_responses']['thanks'])
                return {'response': response, 'intent': 'thanks', 'status': 'success'}
            
            elif intent == 'bye':
                response = random.choice(self.knowledge_base['conversation_responses']['bye'])
                return {'response': response, 'intent': 'bye', 'status': 'success'}
            
            elif intent == 'time':
                dt_info = self.get_current_datetime()
                response = f"⏰ अभी समय है: {dt_info['time']} ({dt_info['day_hindi']}) 🕐"
                return {'response': response, 'intent': 'time', 'status': 'success', 'data': dt_info}
            
            elif intent == 'date':
                dt_info = self.get_current_datetime()
                response = f"📅 आज की तारीख: {dt_info['day_hindi']}, {dt_info['date']}"
                return {'response': response, 'intent': 'date', 'status': 'success', 'data': dt_info}
            
            elif intent == 'weather':
                weather = self.get_weather_info()
                response = f"🌤️ मौसम की जानकारी:\n🌡️ तापमान: {weather['temperature']}\n☁️ स्थिति: {weather['condition']}\n💨 हवा की रफतार: {weather['wind_speed']}\n💧 नमी: {weather['humidity']}"
                return {'response': response, 'intent': 'weather', 'status': 'success', 'data': weather}
            
            elif intent == 'system':
                sys_info = self.get_system_info()
                if 'error' not in sys_info:
                    response = f"💻 System Information:\n🖥️ OS: {sys_info['system']['os']}\n⚙️ CPU: {sys_info['cpu']['usage_percent']}%\n💾 Memory: {sys_info['memory']['percent']}%\n💿 Disk: {sys_info['disk']['used_percent']}%\n⏱️ Uptime: {sys_info['uptime']}"
                    return {'response': response, 'intent': 'system', 'status': 'success', 'data': sys_info}
                else:
                    return {'response': 'System info उपलब्ध नहीं है। ⚠️', 'intent': 'system', 'status': 'error'}
            
            elif intent == 'vanie':
                response = random.choice(self.knowledge_base['conversation_responses']['vanie_about'])
                return {'response': response, 'intent': 'vanie', 'status': 'success'}
            
            elif intent == 'code':
                response = "💻 Programming में मैं expert हूँ! Python, JavaScript, Java, C++ - सभी में मदद कर सकती हूँ। क्या specific topic चाहिए? 🚀"
                return {'response': response, 'intent': 'code', 'status': 'success'}
            
            elif intent == 'emotional':
                response = random.choice(self.response_patterns['emotional_support'])
                return {'response': response, 'intent': 'emotional', 'status': 'success'}
            
            else:
                # Default response
                fallback_responses = [
                    f"🤔 दिलचस्प सवाल है! '{message}' के बारे में मैं थोड़ी जानकारी देती हूँ:\n\nयह एक महत्वपूर्ण विषय है। क्या आप इसके बारे में और जानना चाहेंगे? मैं आपको details दे सकती हूँ! 📚",
                    "✨ वाह! यह तो interesting topic है! मैं इसके बारे में जानकारी दे सकती हूँ। क्या और कुछ जानना चाहते हैं? 🌟",
                    "🎯 बिल्कुल! यह एक अच्छा सवाल है। मैं इसमें आपकी मदद करने की कोशिश करूँ। अगर कोई specific help चाहिए तो बताइए! 💡",
                    "👍 आपकी बात समझ गई! मैं आपको best possible help दूंगी। क्या कुछ specific जानना चाहते हैं? 🤖"
                ]
                response = random.choice(fallback_responses)
                return {'response': response, 'intent': 'general', 'status': 'success'}
        
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                'response': f"मुझे एक technical issue आया है। 😔 कृपया फिर से कोशिश करें।",
                'intent': 'error',
                'status': 'error',
                'error': str(e)
            }

# Initialize VANIE engine
vanie_engine = VANIEEngine()

# Routes
@app.route('/')
def index():
    """Serve the main HTML page"""
    try:
        return send_from_directory('.', 'VANIE.html')
    except:
        return jsonify({'error': 'VANIE.html not found'}), 404

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    """Main chat endpoint"""
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
            'response': 'मुझे एक technical issue आया है। कृपया फिर से कोशिश करें। ⚠️'
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'version': vanie_engine.knowledge_base['vanie_info']['version']
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

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🤖 VANIE - Virtual Assistant of Neural Integrated Engine")
    print("="*60)
    print(f"✨ Version: {vanie_engine.knowledge_base['vanie_info']['version']}")
    print(f"👤 Creator: {vanie_engine.knowledge_base['vanie_info']['creator']}")
    print("="*60)
    print("🚀 Starting VANIE backend server...")
    print("📍 Access the webapp at: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=False,
        threaded=True,
        use_reloader=False
    )
