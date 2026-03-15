# VANIE Frontend Integration Script
# Update your VANIE.html with this enhanced generateResponse function

# Instructions:
# 1. Open VANIE.html
# 2. Find the existing generateResponse function (around line 2717)
# 3. Replace it completely with the code below
# 4. Add the new checkBackendStatus function
# 5. Update the init function to include backend check

# Enhanced generateResponse Function with Backend Integration
async generateResponse(userInput) {
    try {
        // Show typing indicator
        this.showTyping();
        
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
        
        // Hide typing indicator
        this.hideTyping();
        
        if (data.status === 'success') {
            // Log the response details for debugging
            console.log('AI Response Details:', {
                category: data.category,
                confidence: data.confidence,
                matched_keywords: data.matched_keywords,
                context_length: data.context_length
            });
            
            return data.response;
        } else {
            console.error('Backend error:', data.error);
            this.showNotification('Backend error: ' + data.error, 'error');
            return this.getRandomResponse(this.responses.fallback);
        }
    } catch (error) {
        console.error('Network error:', error);
        this.hideTyping();
        
        // Check if backend is running
        if (error.message.includes('Failed to fetch')) {
            this.showNotification('Backend not available. Using fallback responses. ⚠️', 'error');
        }
        
        // Fallback to existing responses if backend is unavailable
        return this.getRandomResponse(this.responses.fallback);
    }
}

# New Backend Status Check Function
async checkBackendStatus() {
    try {
        const response = await fetch('http://localhost:5000/api/health');
        const data = await response.json();
        
        if (data.status === 'healthy') {
            console.log('Backend connected successfully:', data);
            this.showNotification('Connected to VANIE AI Backend! 🤖', 'success');
            
            // Update status indicator
            const statusDot = document.querySelector('.status-dot');
            if (statusDot) {
                statusDot.style.background = 'rgba(0, 255, 0, 0.8)'; // Green
            }
            
            return true;
        }
    } catch (error) {
        console.error('Backend connection failed:', error);
        this.showNotification('Backend not available. Using fallback responses. ⚠️', 'error');
        
        // Update status indicator
        const statusDot = document.querySelector('.status-dot');
        if (statusDot) {
            statusDot.style.background = 'rgba(255, 59, 48, 0.8)'; // Red
        }
        
        return false;
    }
}

# Enhanced init Function Update
# Find the existing init() function and replace it with:
async init() {
    this.loadSettings();
    this.loadChatHistory();
    this.initVoiceRecognition();
    this.setupEventListeners();
    
    // Check backend connection first
    const backendAvailable = await this.checkBackendStatus();
    
    if (backendAvailable) {
        console.log('🚀 VANIE is running with Python Backend AI!');
    } else {
        console.log('⚠️ VANIE is running with fallback responses only.');
    }
    
    this.sendInitialMessage();
}

# Additional Helper Function for Backend Debugging
addBackendDebugInfo() {
    // Add this function to help debug backend integration
    const debugInfo = {
        backendUrl: 'http://localhost:5000',
        endpoints: {
            chat: '/api/chat',
            health: '/api/health',
            history: '/api/history',
            clear: '/api/clear'
        },
        status: 'checking...'
    };
    
    console.log('🔍 VANIE Backend Debug Info:', debugInfo);
    return debugInfo;
}

# CSS for Backend Status Indicator
# Add this CSS to your existing styles
.backend-status-indicator {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin-left: 8px;
}

.backend-status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.4);
    transition: all 0.3s ease;
}

.backend-status-dot.connected {
    background: rgba(0, 255, 0, 0.8);
    box-shadow: 0 0 4px rgba(0, 255, 0, 0.3);
}

.backend-status-dot.disconnected {
    background: rgba(255, 59, 48, 0.8);
    box-shadow: 0 0 4px rgba(255, 59, 48, 0.3);
}

.backend-status-text {
    font-size: 11px;
    color: var(--text-secondary);
    font-weight: 500;
}

# HTML Update for Status Indicator
# Find the bot-status div and update it:
<div class="bot-status">
    <span class="backend-status-indicator">
        <span class="backend-status-dot" id="backendStatusDot"></span>
        <span class="backend-status-text" id="backendStatusText">Checking...</span>
    </span>
    <span id="statusText">Online</span>
</div>
