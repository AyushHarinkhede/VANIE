# VANIE AI Backend - Setup and Integration Guide
# Complete Python Backend for VANIE Web Application

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install flask flask-cors
```

### 2. Run the Backend
```bash
python vanie_ai_backend.py
```

### 3. Access API
- **Backend URL**: http://localhost:5000
- **API Docs**: http://localhost:5000
- **Health Check**: http://localhost:5000/api/health

## 🔗 Frontend Integration

### Step 1: Update Frontend JavaScript

Replace the existing `generateResponse` function in VANIE.html:

```javascript
// Replace the entire generateResponse function with this:
async generateResponse(userInput) {
    try {
        // Call Python backend API
        const response = await fetch('http://localhost:5000/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: userInput,
                session_id: this.state.userId || 'default'
            })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            return data.response;
        } else {
            console.error('Backend error:', data.error);
            return this.getRandomResponse(this.responses.fallback);
        }
    } catch (error) {
        console.error('Network error:', error);
        // Fallback to existing responses if backend is unavailable
        return this.getRandomResponse(this.responses.fallback);
    }
}
```

### Step 2: Add Backend Connection Status

Add this function to check backend status:

```javascript
async checkBackendStatus() {
    try {
        const response = await fetch('http://localhost:5000/api/health');
        const data = await response.json();
        
        if (data.status === 'healthy') {
            this.showNotification('Connected to VANIE AI Backend! 🤖', 'success');
            return true;
        }
    } catch (error) {
        this.showNotification('Backend not available. Using fallback responses. ⚠️', 'error');
        return false;
    }
}

// Add to init() function:
async init() {
    this.loadSettings();
    this.loadChatHistory();
    this.initVoiceRecognition();
    this.setupEventListeners();
    
    // Check backend connection
    await this.checkBackendStatus();
    
    this.sendInitialMessage();
}
```

## 🧠 Algorithm Explanation

### 1. Keyword Analysis Process

```python
def _analyze_input(self, user_input: str) -> Dict[str, Any]:
    """
    Step 1: Convert input to lowercase
    Step 2: Check each category for keyword matches
    Step 3: Calculate confidence scores based on:
        - Number of matching keywords
        - Position of keywords in input
        - Completeness of match
    Step 4: Return analysis results
    """
```

### 2. Category Selection Logic

```python
def _select_best_category(self, analysis: Dict[str, Any]) -> Optional[str]:
    """
    Step 1: Sort matched categories by score and confidence
    Step 2: Select highest scoring category
    Step 3: Return category name or None if no matches
    """
```

### 3. Response Generation

```python
def _get_contextual_response(self, category: str, user_input: str) -> str:
    """
    Step 1: Get base responses for category
    Step 2: Add contextual information based on specific keywords
    Step 3: Return random response from category
    """
```

## 📊 API Endpoints

### 1. POST /api/chat
**Purpose**: Send message and get AI response

**Request**:
```json
{
    "message": "Hello VANIE",
    "session_id": "user123"
}
```

**Response**:
```json
{
    "response": "नमस्ते! 🙏 मैं VANIE हूँ...",
    "category": "greetings",
    "confidence": 0.95,
    "matched_keywords": [["hello", "नमस्ते"]],
    "context_length": 5,
    "session_id": "user123",
    "timestamp": "2024-03-16T12:00:00",
    "status": "success"
}
```

### 2. GET /api/history
**Purpose**: Get conversation history

**Response**:
```json
{
    "history": [
        {
            "user_input": "Hello",
            "ai_response": "नमस्ते! मैं VANIE हूँ...",
            "timestamp": "2024-03-16T12:00:00"
        }
    ],
    "session_id": "user123",
    "total_messages": 10,
    "status": "success"
}
```

### 3. DELETE /api/clear
**Purpose**: Clear conversation context

**Response**:
```json
{
    "message": "Conversation context cleared successfully",
    "session_id": "user123",
    "status": "success"
}
```

### 4. GET /api/health
**Purpose**: Check API health status

**Response**:
```json
{
    "status": "healthy",
    "service": "VANIE AI Backend",
    "version": "1.0.0",
    "timestamp": "2024-03-16T12:00:00",
    "features": {
        "keyword_matching": true,
        "context_awareness": true,
        "multi_language": true,
        "session_management": true
    }
}
```

## 🎯 Advanced Features

### 1. Multi-Keyword Detection
- Detects multiple keywords in single input
- Prioritizes based on confidence scores
- Handles complex queries

### 2. Context Awareness
- Maintains conversation history
- Uses context for better responses
- Limits to last 10 messages

### 3. Session Management
- Tracks user sessions
- Maintains per-user conversation history
- Supports multiple simultaneous users

### 4. Fallback System
- Graceful degradation when no keywords match
- Intelligent default responses
- Error handling for network issues

## 🔧 Configuration Options

### Customizing Keywords
Edit the `_initialize_knowledge_base()` method:

```python
'custom_category': {
    'keywords': ['keyword1', 'keyword2', 'keyword3'],
    'responses': [
        "Response 1 for custom category",
        "Response 2 for custom category"
    ]
}
```

### Adding Languages
Extend keyword lists with different languages:

```python
'greetings': {
    'keywords': [
        'hello', 'hi', 'namaste',  # English
        'नमस्ते', 'हाय',           # Hindi
        'bonjour', 'salut'          # French
    ],
    'responses': [...]
}
```

## 🚀 Production Deployment

### 1. Environment Setup
```bash
# Set environment variables
export FLASK_ENV=production
export FLASK_PORT=5000
```

### 2. Using Gunicorn (Recommended)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 vanie_ai_backend:app
```

### 3. Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY vanie_ai_backend.py .
RUN pip install flask flask-cors
EXPOSE 5000
CMD ["python", "vanie_ai_backend.py"]
```

## 🔍 Testing the Backend

### 1. Test with curl
```bash
# Test chat endpoint
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello VANIE", "session_id": "test"}'

# Test health endpoint
curl http://localhost:5000/api/health
```

### 2. Test with Python
```python
import requests

# Test chat
response = requests.post('http://localhost:5000/api/chat', 
    json={'message': 'Hello VANIE', 'session_id': 'test'})
print(response.json())

# Test health
health = requests.get('http://localhost:5000/api/health')
print(health.json())
```

## 🎨 Frontend Integration Complete

### Final Integration Steps:
1. ✅ Backend running on localhost:5000
2. ✅ Update frontend generateResponse function
3. ✅ Add backend connection check
4. ✅ Test integration
5. ✅ Deploy to production

Your VANIE webapp now has a powerful Python backend with intelligent keyword matching, context awareness, and multi-language support! 🚀
