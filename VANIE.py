#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VANIE - Virtual Assistant of Neural Integrated Engine
Advanced Backend System with Real-time Information Capabilities
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
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import logging
from typing import Dict, Any, List
import random
import math

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class VANIEEngine:
    """Main VANIE Engine with Advanced Real-time Capabilities"""
    
    def __init__(self):
        self.user_name = "Guest"  # Will be updated based on conversation
        self.conversation_context = []
        self.weather_cache = {}
        self.system_info_cache = None
        self.last_system_update = 0
        self.personalization_data = {}
        
        # Initialize knowledge base
        self.knowledge_base = self._initialize_knowledge_base()
        
        # Response patterns for natural conversation
        self.response_patterns = {
            'greetings': [
                "नमस्ते {name}! मैं VANIE हूँ, आपकी AI assistant! कैसे मदद कर सकती हूँ? 😊",
                "Hello {name}! I'm VANIE, how can I assist you today? 🤖",
                "Hi {name}! VANIE at your service! What can I do for you? ✨"
            ],
            'time_responses': [
                "अभी समय है {time}, {date} को 🕐",
                "Current time is {time}, on {date} ⏰",
                "Right now it's {time}, {date} 📅"
            ],
            'weather_responses': [
                "आज का मौसम: {weather} 🌡️",
                "Today's weather: {weather} 🌤️",
                "Weather report: {weather} ☁️"
            ]
        }
    
    def _initialize_knowledge_base(self) -> Dict[str, Any]:
        """Initialize comprehensive knowledge base"""
        return {
            'vanie_info': {
                'full_form': "Virtual Assistant of Neural Integrated Engine",
                'creator': "Ayush Harinkhede",
                'version': "2.0",
                'capabilities': [
                    "Real-time Information",
                    "System Monitoring", 
                    "Weather Updates",
                    "Natural Conversation",
                    "Programming Help",
                    "Mathematical Calculations",
                    "Date & Time Services"
                ]
            },
            'general_knowledge': {
                'programming_languages': ['Python', 'JavaScript', 'Java', 'C++', 'C#', 'Ruby', 'Go', 'Rust'],
                'frameworks': ['React', 'Angular', 'Vue.js', 'Django', 'Flask', 'FastAPI', 'Node.js'],
                'algorithms': ['Binary Search', 'QuickSort', 'MergeSort', 'Dijkstra', 'Floyd-Warshall'],
                'subjects': ['Physics', 'Chemistry', 'Mathematics', 'Computer Science', 'History', 'Geography']
            },
            'conversation_patterns': {
                'name_questions': [
                    r'(?i)(what is your|what\'s your|tell me your) name',
                    r'(?i)(who are you|what are you)',
                    r'(?i)(आपका नाम क्या है|तुम्हारा नाम क्या है)'
                ],
                'time_questions': [
                    r'(?i)(what time|current time|समय क्या है|अभी कितना बजा)',
                    r'(?i)(आज का समय|अभी समय)'
                ],
                'date_questions': [
                    r'(?i)(what date|today\'s date|आज की तारीख|आज कौन सी तारीख है)',
                    r'(?i)(दिनांक|तारीख)'
                ],
                'weather_questions': [
                    r'(?i)(weather|मौसम|temperature|तापमान)',
                    r'(?i)(how\'s the weather|आज का मौसम कैसा है)'
                ],
                'system_questions': [
                    r'(?i)(system|computer|pc|कंप्यूटर)',
                    r'(?i)(ram|memory|cpu|storage|disk)'
                ],
                'vanie_questions': [
                    r'(?i)(vanie|vanie क्या है|vanie full form)',
                    r'(?i)(who created you|आपको किसने बनाया)'
                ]
            }
        }
    
    def get_current_datetime(self) -> Dict[str, str]:
        """Get current date and time information"""
        now = datetime.datetime.now()
        
        # Hindi days and months
        hindi_days = ['सोमवार', 'मंगलवार', 'बुधवार', 'गुरुवार', 'शुक्रवार', 'शनिवार', 'रविवार']
        hindi_months = ['जनवरी', 'फरवरी', 'मार्च', 'अप्रैल', 'मई', 'जून', 
                       'जुलाई', 'अगस्त', 'सितंबर', 'अक्टूबर', 'नवंबर', 'दिसंबर']
        
        return {
            'time': now.strftime('%I:%M:%S %p'),
            'time_24': now.strftime('%H:%M:%S'),
            'date': now.strftime('%d-%m-%Y'),
            'date_us': now.strftime('%m-%d-%Y'),
            'day': now.strftime('%A'),
            'day_hindi': hindi_days[now.weekday()],
            'month': now.strftime('%B'),
            'month_hindi': hindi_months[now.month - 1],
            'year': str(now.year),
            'formatted': now.strftime('%A, %B %d, %Y'),
            'formatted_hindi': f"{hindi_days[now.weekday()]}, {hindi_months[now.month - 1]} {now.day}, {now.year}",
            'timestamp': str(int(now.timestamp())),
            'iso_format': now.isoformat()
        }
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        current_time = time.time()
        
        # Cache system info for 60 seconds
        if self.system_info_cache and (current_time - self.last_system_update) < 60:
            return self.system_info_cache
        
        try:
            # Basic system info
            system_info = {
                'platform': platform.system(),
                'platform_version': platform.version(),
                'platform_release': platform.release(),
                'architecture': platform.machine(),
                'hostname': socket.gethostname(),
                'processor': platform.processor(),
                'python_version': platform.python_version(),
            }
            
            # CPU Information
            cpu_info = {
                'physical_cores': psutil.cpu_count(logical=False),
                'total_cores': psutil.cpu_count(logical=True),
                'max_frequency': psutil.cpu_freq().max if psutil.cpu_freq() else 0,
                'current_frequency': psutil.cpu_freq().current if psutil.cpu_freq() else 0,
                'cpu_usage_percent': psutil.cpu_percent(interval=1),
                'cpu_per_core': psutil.cpu_percent(percpu=True)
            }
            
            # Memory Information
            memory = psutil.virtual_memory()
            memory_info = {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'percentage': memory.percent,
                'total_gb': round(memory.total / (1024**3), 2),
                'available_gb': round(memory.available / (1024**3), 2),
                'used_gb': round(memory.used / (1024**3), 2)
            }
            
            # Disk Information
            disk = psutil.disk_usage('/')
            disk_info = {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percentage': (disk.used / disk.total) * 100,
                'total_gb': round(disk.total / (1024**3), 2),
                'used_gb': round(disk.used / (1024**3), 2),
                'free_gb': round(disk.free / (1024**3), 2)
            }
            
            # Network Information
            network_info = {}
            try:
                network_info = psutil.net_if_addrs()
                network_stats = psutil.net_io_counters()
                network_info['bytes_sent'] = network_stats.bytes_sent
                network_info['bytes_recv'] = network_stats.bytes_recv
            except:
                pass
            
            # Boot time
            boot_time = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')
            
            self.system_info_cache = {
                'system': system_info,
                'cpu': cpu_info,
                'memory': memory_info,
                'disk': disk_info,
                'network': network_info,
                'boot_time': boot_time,
                'uptime': str(datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time()))
            }
            
            self.last_system_update = current_time
            return self.system_info_cache
            
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {'error': 'Unable to retrieve system information'}
    
    def get_weather_info(self, location: str = "Delhi") -> Dict[str, Any]:
        """Get weather information (mock implementation - can be extended with real API)"""
        # Check cache first (cache for 30 minutes)
        cache_key = f"{location}_{datetime.datetime.now().strftime('%Y%m%d%H')}"
        if cache_key in self.weather_cache:
            return self.weather_cache[cache_key]
        
        # Mock weather data (replace with real API call)
        mock_weather = {
            'location': location,
            'temperature': f"{random.randint(18, 35)}°C",
            'feels_like': f"{random.randint(16, 37)}°C",
            'humidity': f"{random.randint(30, 80)}%",
            'wind_speed': f"{random.randint(5, 25)} km/h",
            'condition': random.choice(['Sunny', 'Partly Cloudy', 'Cloudy', 'Clear', 'Light Rain']),
            'visibility': f"{random.randint(5, 10)} km",
            'pressure': f"{random.randint(1000, 1020)} mb",
            'uv_index': str(random.randint(1, 10)),
            'last_updated': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.weather_cache[cache_key] = mock_weather
        return mock_weather
    
    def detect_user_intent(self, message: str) -> str:
        """Detect user intent from message"""
        message_lower = message.lower()
        
        # Check for different types of questions
        patterns = self.knowledge_base['conversation_patterns']
        
        # Name/Identity questions
        for pattern in patterns['name_questions']:
            if re.search(pattern, message):
                return 'name_query'
        
        # Time questions
        for pattern in patterns['time_questions']:
            if re.search(pattern, message):
                return 'time_query'
        
        # Date questions
        for pattern in patterns['date_questions']:
            if re.search(pattern, message):
                return 'date_query'
        
        # Weather questions
        for pattern in patterns['weather_questions']:
            if re.search(pattern, message):
                return 'weather_query'
        
        # System questions
        for pattern in patterns['system_questions']:
            if re.search(pattern, message):
                return 'system_query'
        
        # VANIE specific questions
        for pattern in patterns['vanie_questions']:
            if re.search(pattern, message):
                return 'vanie_query'
        
        # Check for programming/coding help
        programming_keywords = ['code', 'program', 'algorithm', 'python', 'javascript', 'java', 'coding']
        if any(keyword in message_lower for keyword in programming_keywords):
            return 'programming_help'
        
        # Check for mathematical calculations
        if any(char in message for char in '+-*/^()') and any(char.isdigit() for char in message):
            return 'math_calculation'
        
        # Default to general conversation
        return 'general_conversation'
    
    def generate_response(self, message: str, user_context: Dict = None) -> Dict[str, Any]:
        """Generate intelligent response based on user input"""
        intent = self.detect_user_intent(message)
        datetime_info = self.get_current_datetime()
        
        # Update conversation context
        self.conversation_context.append({
            'message': message,
            'intent': intent,
            'timestamp': datetime_info['timestamp']
        })
        
        # Keep only last 10 messages in context
        self.conversation_context = self.conversation_context[-10:]
        
        response = {
            'intent': intent,
            'timestamp': datetime_info['timestamp'],
            'context_updated': True
        }
        
        try:
            if intent == 'name_query':
                response['response'] = self._handle_name_query()
                response['data'] = {'name': 'VANIE', 'full_form': self.knowledge_base['vanie_info']['full_form']}
                
            elif intent == 'time_query':
                response['response'] = self._handle_time_query(datetime_info)
                response['data'] = {'datetime': datetime_info}
                
            elif intent == 'date_query':
                response['response'] = self._handle_date_query(datetime_info)
                response['data'] = {'datetime': datetime_info}
                
            elif intent == 'weather_query':
                weather = self.get_weather_info()
                response['response'] = self._handle_weather_query(weather)
                response['data'] = {'weather': weather}
                
            elif intent == 'system_query':
                system = self.get_system_info()
                response['response'] = self._handle_system_query(system)
                response['data'] = {'system': system}
                
            elif intent == 'vanie_query':
                response['response'] = self._handle_vanie_query()
                response['data'] = {'vanie_info': self.knowledge_base['vanie_info']}
                
            elif intent == 'programming_help':
                response['response'] = self._handle_programming_help(message)
                response['data'] = {'programming_languages': self.knowledge_base['general_knowledge']['programming_languages']}
                
            elif intent == 'math_calculation':
                response['response'] = self._handle_math_calculation(message)
                response['data'] = {'calculation': message}
                
            else:
                response['response'] = self._handle_general_conversation(message)
                response['data'] = {'conversation_type': 'general'}
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            response['response'] = "मुझे अपनी प्रतिक्रिया उत्पन्न करने में कठिनाई हो रही है। कृपया फिर से प्रयास करें।"
            response['error'] = str(e)
        
        return response
    
    def _handle_name_query(self) -> str:
        """Handle name/identity queries"""
        name_response = random.choice(self.response_patterns['greetings']).format(name=self.user_name)
        vanie_info = self.knowledge_base['vanie_info']
        return f"{name_response}\n\nमैं {vanie_info['full_form']} हूँ, जिसे {vanie_info['creator']} ने बनाया है। मैं आपको real-time information, programming help, और बहुत कुछ में मदद कर सकती हूँ! 🤖✨"
    
    def _handle_time_query(self, datetime_info: Dict) -> str:
        """Handle time queries"""
        time_response = random.choice(self.response_patterns['time_responses']).format(
            time=datetime_info['time'],
            date=datetime_info['formatted_hindi']
        )
        return f"{time_response}\n\nविस्तृत जानकारी:\n• समय: {datetime_info['time']} ({datetime_info['time_24']} 24-घंटे प्रारूप में)\n• दिन: {datetime_info['day_hindi']}\n• तारीख: {datetime_info['date']}"
    
    def _handle_date_query(self, datetime_info: Dict) -> str:
        """Handle date queries"""
        return f"आज की तारीख है: {datetime_info['formatted_hindi']} 📅\n\nअन्य प्रारूप:\n• DD-MM-YYYY: {datetime_info['date']}\n• MM-DD-YYYY: {datetime_info['date_us']}\n• ISO: {datetime_info['iso_format']}\n\nआज {datetime_info['day_hindi']} है और महीना {datetime_info['month_hindi']} है।"
    
    def _handle_weather_query(self, weather: Dict) -> str:
        """Handle weather queries"""
        weather_response = random.choice(self.response_patterns['weather_responses']).format(
            weather=f"{weather['condition']}, तापमान {weather['temperature']}"
        )
        return f"{weather_response}\n\nविस्तृत मौसम जानकारी ({weather['location']}):\n• तापमान: {weather['temperature']} (महसूस {weather['feels_like']})\n• हालत: {weather['condition']}\n• नमी: {weather['humidity']}\n• हवा: {weather['wind_speed']}\n• दृश्यता: {weather['visibility']}\n• दबाव: {weather['pressure']}\n• UV इंडेक्स: {weather['uv_index']}"
    
    def _handle_system_query(self, system: Dict) -> str:
        """Handle system information queries"""
        if 'error' in system:
            return "सिस्टम जानकारी प्राप्त करने में त्रुटि। कृपया बाद में पुनः प्रयास करें।"
        
        sys_info = system['system']
        cpu_info = system['cpu']
        mem_info = system['memory']
        disk_info = system['disk']
        
        return f"""🖥️ **सिस्टम जानकारी:**

**बेसिक जानकारी:**
• प्लेटफॉर्म: {sys_info['platform']} {sys_info['platform_release']}
• होस्टनेम: {sys_info['hostname']}
• प्रोसेसर: {sys_info['processor']}
• Python वर्जन: {sys_info['python_version']}

**CPU जानकारी:**
• कोर: {cpu_info['total_cores']} (फिजिकल: {cpu_info['physical_cores']})
• उपयोग: {cpu_info['cpu_usage_percent']}%
• फ्रीक्वेंसी: {cpu_info['current_frequency']:.2f} MHz

**मेमोरी जानकारी:**
• कुल: {mem_info['total_gb']} GB
• उपयोग में: {mem_info['used_gb']} GB ({mem_info['percentage']}%)
• उपलब्ध: {mem_info['available_gb']} GB

**डिस्क जानकारी:**
• कुल: {disk_info['total_gb']} GB
• उपयोग में: {disk_info['used_gb']} GB ({disk_info['percentage']:.1f}%)
• खाली: {disk_info['free_gb']} GB

**अपटाइम:** {system['uptime']}"""
    
    def _handle_vanie_query(self) -> str:
        """Handle VANIE-specific queries"""
        vanie_info = self.knowledge_base['vanie_info']
        capabilities = '\n'.join([f"• {cap}" for cap in vanie_info['capabilities']])
        
        return f"""🤖 **VANIE - Virtual Assistant of Neural Integrated Engine**

**पूरा नाम:** {vanie_info['full_form']}
**क्रिएटर:** {vanie_info['creator']}
**वर्जन:** {vanie_info['version']}

**क्षमताएं:**
{capabilities}

मैं आपको real-time information, system monitoring, weather updates, programming help, और natural conversation में मदद कर सकती हूँ! कुछ भी पूछने के लिए तैयार हूँ! ✨"""
    
    def _handle_programming_help(self, message: str) -> str:
        """Handle programming help requests"""
        languages = self.knowledge_base['general_knowledge']['programming_languages']
        frameworks = self.knowledge_base['general_knowledge']['frameworks']
        algorithms = self.knowledge_base['general_knowledge']['algorithms']
        
        return f"""💻 **प्रोग्रामिंग मदद!**

मैं निम्नलिखित में विशेषज्ञता रखती हूँ:

**प्रोग्रामिंग भाषाएं:**
{', '.join(languages)}

**फ्रेमवर्क:**
{', '.join(frameworks)}

**एल्गोरिदम:**
{', '.join(algorithms)}

कौन सा टॉपिक चाहिए? Algorithm explanation, code example, debugging help - कुछ भी पूछ सकते हैं! 🚀"""
    
    def _handle_math_calculation(self, message: str) -> str:
        """Handle mathematical calculations"""
        try:
            # Safe math evaluation (basic operations only)
            allowed_chars = set('0123456789+-*/().^ ')
            if not all(c in allowed_chars for c in message):
                return "केवल basic mathematical operations (+, -, *, /, ^, parentheses) की अनुमति है।"
            
            # Replace ^ with ** for power
            expression = message.replace('^', '**')
            result = eval(expression)
            
            return f"""🧮 **गणितीय गणना:**

**व्यंजक:** {message}
**परिणाम:** {result}

विस्तृत गणना चाहिए? Step-by-step explanation दे सकती हूँ! 📚"""
            
        except Exception as e:
            return f"गणना में त्रुटि: {str(e)}. कृपया correct mathematical expression डालें।"
    
    def _handle_general_conversation(self, message: str) -> str:
        """Handle general conversation"""
        general_responses = [
            "यह दिलचस्प बातचीत है! मुझे और बताएं। 😊",
            "मैं आपकी बात समझ गई। और क्या जानना चाहते हैं?",
            "Great point! क्या मैं आपको किसी specific topic में मदद कर सकती हूँ?",
            "मैं आपकी मदद के लिए यहाँ हूँ! Programming, math, weather, system info - कुछ भी पूछें! 🤖"
        ]
        
        return random.choice(general_responses)

# Initialize VANIE Engine
vanie_engine = VANIEEngine()

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('VANIE.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
        
        user_message = data['message']
        user_context = data.get('context', {})
        
        # Update user name if provided
        if 'user_name' in user_context:
            vanie_engine.user_name = user_context['user_name']
        
        # Generate response
        response = vanie_engine.generate_response(user_message, user_context)
        
        return jsonify({
            'response': response['response'],
            'intent': response['intent'],
            'data': response.get('data', {}),
            'timestamp': response['timestamp']
        })
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/info/datetime', methods=['GET'])
def get_datetime():
    """Get current date and time"""
    return jsonify(vanie_engine.get_current_datetime())

@app.route('/info/system', methods=['GET'])
def get_system():
    """Get system information"""
    return jsonify(vanie_engine.get_system_info())

@app.route('/info/weather', methods=['GET'])
def get_weather():
    """Get weather information"""
    location = request.args.get('location', 'Delhi')
    return jsonify(vanie_engine.get_weather_info(location))

@app.route('/info/vanie', methods=['GET'])
def get_vanie_info():
    """Get VANIE information"""
    return jsonify(vanie_engine.knowledge_base['vanie_info'])

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'version': vanie_engine.knowledge_base['vanie_info']['version']
    })

def start_server(host='127.0.0.1', port=5000, debug=False):
    """Start the VANIE server"""
    print(f"""
🚀 VANIE Server Starting...
📍 Host: {host}
🔌 Port: {port}
🤖 Version: {vanie_engine.knowledge_base['vanie_info']['version']}
📅 Started at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """)
    
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    start_server(debug=True)
