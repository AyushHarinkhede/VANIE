# VANIE - Virtual Assistant of Neural Integrated Engine

एक advanced AI assistant जो real-time information, system monitoring, weather updates, और natural conversation प्रदान करता है।

## 🚀 Features

### Real-time Information
- **Date & Time**: Current date, time, day information in both English and Hindi
- **Weather**: Weather updates with temperature, humidity, wind speed
- **System Information**: CPU, Memory, Disk usage, and system details
- **VANIE Info**: Complete information about VANIE assistant

### Intelligent Conversation
- **Natural Language Processing**: Smart intent detection
- **Context Awareness**: Remembers conversation history
- **Multilingual Support**: Hindi and English responses
- **Programming Help**: Code examples, algorithms, debugging
- **Mathematical Calculations**: Safe math expression evaluation

### Advanced Backend
- **Flask API**: RESTful endpoints for all services
- **Caching**: Efficient caching for weather and system info
- **Error Handling**: Comprehensive error management
- **Performance Optimized**: Fast response times

## 📋 Prerequisites

- Python 3.7 or higher
- Modern web browser (Chrome, Firefox, Edge, Safari)
- 4GB+ RAM recommended
- Internet connection (for weather API)

## 🛠️ Installation & Setup

### 1. Clone/Download the Project
```bash
git clone <repository-url>
cd VANIE👾
```

### 2. Automatic Setup (Recommended)
Run the automated setup script:
```bash
start_backend.bat
```

This script will:
- Check Python installation
- Create virtual environment
- Install dependencies
- Start the backend server

### 3. Manual Setup
If you prefer manual setup:

#### Create Virtual Environment
```bash
python -m venv venv
```

#### Activate Virtual Environment
**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Start Backend Server
```bash
python VANIE.py
```

## 🌐 Running the Application

### Method 1: Using the HTML File
1. Start the backend server first
2. Open `VANIE.html` in your web browser
3. The webapp will automatically connect to the backend

### Method 2: Using Flask Server
The backend also serves the HTML file:
1. Run `python VANIE.py`
2. Visit `http://127.0.0.1:5000` in your browser

## 📡 API Endpoints

### Main Chat Endpoint
```
POST /chat
Content-Type: application/json

{
    "message": "What time is it?",
    "context": {
        "user_name": "John",
        "session_id": "user123"
    }
}
```

### Information Endpoints
- `GET /info/datetime` - Get current date and time
- `GET /info/system` - Get system information
- `GET /info/weather?location=Delhi` - Get weather information
- `GET /info/vanie` - Get VANIE information
- `GET /health` - Health check

## 💬 Usage Examples

### Time & Date Queries
- "What time is it?"
- "आज की तारीख क्या है?"
- "समय क्या है?"

### Weather Information
- "How's the weather?"
- "आज का मौसम कैसा है?"
- "What's the temperature?"

### System Information
- "Show me system info"
- "कंप्यूटर की जानकारी"
- "How much RAM is available?"

### VANIE Information
- "What is VANIE?"
- "VANIE full form"
- "Who created you?"

### Programming Help
- "Python code for QuickSort"
- "Explain binary search"
- "JavaScript array methods"

### Math Calculations
- "2 + 2 * 3"
- "sqrt(16) + 5"
- "2^3 + 4*5"

## 🔧 Configuration

### Weather API
Currently using mock weather data. To integrate real weather API:

1. Sign up for weather API service (OpenWeatherMap, etc.)
2. Update `get_weather_info()` method in `VANIE.py`
3. Add your API key

### Customization
- Modify `response_patterns` in `VANIE.py` for custom responses
- Update `knowledge_base` for domain-specific information
- Customize CSS in `VANIE.html` for different themes

## 🏗️ Architecture

### Backend (Python/Flask)
```
VANIE.py
├── VANIEEngine (Main Class)
├── Intent Detection
├── Response Generation
├── System Information
├── Weather Service
└── API Endpoints
```

### Frontend (HTML/JavaScript)
```
VANIE.html
├── Modern UI Design
├── Real-time Chat Interface
├── Voice Input Support
├── File Upload
└── Backend Integration
```

## 🐛 Troubleshooting

### Common Issues

#### Server Not Starting
- Check Python installation: `python --version`
- Verify dependencies: `pip list`
- Check port availability (default: 5000)

#### Connection Errors
- Ensure backend server is running
- Check firewall settings
- Verify CORS configuration

#### Performance Issues
- Increase system RAM
- Close unnecessary applications
- Check CPU usage

### Debug Mode
Enable debug mode in `VANIE.py`:
```python
if __name__ == '__main__':
    start_server(debug=True)
```

## 📝 Development

### Adding New Features
1. Update intent detection in `detect_user_intent()`
2. Add response handler in `_handle_*()` methods
3. Update frontend if needed
4. Test thoroughly

### Contributing
1. Fork the repository
2. Create feature branch
3. Make changes
4. Test all features
5. Submit pull request

## 📄 License

This project is developed by Ayush Harinkhede. Contact for licensing information.

## 🤝 Support

For issues and support:
- Check troubleshooting section
- Review logs for errors
- Ensure all dependencies are installed
- Verify network connectivity

## 🔄 Updates

### Version 2.0 Features
- ✅ Real-time system monitoring
- ✅ Enhanced weather service
- ✅ Mathematical calculations
- ✅ Improved conversation context
- ✅ Better error handling
- ✅ Performance optimizations

### Planned Features
- 🔄 Real weather API integration
- 🔄 Voice output/speech synthesis
- 🔄 File analysis capabilities
- 🔄 Multi-user support
- 🔄 Database integration
- 🔄 Mobile app support

---

**VANIE - Virtual Assistant of Neural Integrated Engine**
*Created by Ayush Harinkhede* 🚀
