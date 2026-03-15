// VANIE Advanced Frontend Integration
// Complete JavaScript for HTML integration with typing effect and emotion handling

class VANIEFrontend {
    constructor() {
        this.apiBaseUrl = 'http://localhost:5000';
        this.sessionId = this.generateSessionId();
        this.isTyping = false;
        this.currentTypingTimeout = null;
    }
    
    generateSessionId() {
        return 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    async sendMessage(userMessage) {
        try {
            // Show typing indicator immediately
            this.showTypingIndicator();
            
            // Send message to backend
            const response = await fetch(`${this.apiBaseUrl}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: userMessage,
                    session_id: this.sessionId
                })
            });
            
            const data = await response.json();
            
            // Hide typing indicator
            this.hideTypingIndicator();
            
            if (data.status === 'success') {
                // Display typing indicator first
                this.displayTypingIndicator(data.typing_indicator);
                
                // Then display actual response with delay
                setTimeout(() => {
                    this.displayResponse(data);
                }, 1500 + Math.random() * 1000); // Random delay between 1.5-2.5 seconds
                
                return data;
            } else {
                throw new Error(data.error || 'Unknown error occurred');
            }
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            this.showError('Failed to connect to VANIE. Please check if the backend is running.');
            throw error;
        }
    }
    
    showTypingIndicator() {
        const typingElement = document.getElementById('typingIndicator');
        if (typingElement) {
            typingElement.style.display = 'flex';
            typingElement.innerHTML = `
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
                <span>VANIE is typing...</span>
            `;
        }
    }
    
    hideTypingIndicator() {
        const typingElement = document.getElementById('typingIndicator');
        if (typingElement) {
            typingElement.style.display = 'none';
        }
    }
    
    displayTypingIndicator(message) {
        const chatContainer = document.getElementById('chatContainer');
        if (!chatContainer) return;
        
        const typingMessage = document.createElement('div');
        typingMessage.className = 'message bot typing-message';
        typingMessage.innerHTML = `
            <div class="message-content">
                <div class="typing-text">${message}</div>
                <div class="typing-dots-small">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
            <div class="message-time">${new Date().toLocaleTimeString()}</div>
        `;
        
        chatContainer.appendChild(typingMessage);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    displayResponse(data) {
        const chatContainer = document.getElementById('chatContainer');
        if (!chatContainer) return;
        
        // Remove typing message if exists
        const typingMessage = chatContainer.querySelector('.typing-message');
        if (typingMessage) {
            typingMessage.remove();
        }
        
        // Create message element
        const messageElement = document.createElement('div');
        messageElement.className = 'message bot';
        
        // Add emotion indicator if available
        let emotionIndicator = '';
        if (data.emotion && data.emotion.emotion !== 'neutral') {
            const emotionIcons = {
                'happy': '😊',
                'sad': '😢',
                'angry': '😠',
                'excited': '🎉'
            };
            emotionIndicator = `<span class="emotion-indicator">${emotionIcons[data.emotion.emotion] || ''}</span>`;
        }
        
        messageElement.innerHTML = `
            <div class="message-content">
                ${emotionIndicator}
                <div class="message-text">${data.response}</div>
                <div class="message-meta">
                    <span class="category-tag">${data.category || 'general'}</span>
                    <span class="confidence-score">Confidence: ${Math.round((data.confidence || 0) * 100)}%</span>
                </div>
            </div>
            <div class="message-time">${new Date().toLocaleTimeString()}</div>
        `;
        
        chatContainer.appendChild(messageElement);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        
        // Show emotion notification
        if (data.emotion && data.emotion.emotion !== 'neutral') {
            this.showEmotionNotification(data.emotion);
        }
    }
    
    showEmotionNotification(emotion) {
        const notification = document.createElement('div');
        notification.className = `emotion-notification ${emotion.emotion}`;
        notification.innerHTML = `
            <span class="emotion-icon">${this.getEmotionIcon(emotion.emotion)}</span>
            <span class="emotion-text">I sense you're feeling ${emotion.emotion}</span>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
    
    getEmotionIcon(emotion) {
        const icons = {
            'happy': '😊',
            'sad': '😢',
            'angry': '😠',
            'excited': '🎉',
            'neutral': '😐'
        };
        return icons[emotion] || '😐';
    }
    
    showError(message) {
        const errorElement = document.createElement('div');
        errorElement.className = 'error-notification';
        errorElement.innerHTML = `
            <span class="error-icon">⚠️</span>
            <span class="error-text">${message}</span>
        `;
        
        document.body.appendChild(errorElement);
        
        setTimeout(() => {
            errorElement.remove();
        }, 5000);
    }
    
    async checkBackendHealth() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/health`);
            const data = await response.json();
            
            if (data.status === 'healthy') {
                this.showConnectionStatus('connected');
                return true;
            } else {
                this.showConnectionStatus('disconnected');
                return false;
            }
        } catch (error) {
            this.showConnectionStatus('disconnected');
            return false;
        }
    }
    
    showConnectionStatus(status) {
        const statusElement = document.getElementById('connectionStatus');
        if (statusElement) {
            if (status === 'connected') {
                statusElement.className = 'connection-status connected';
                statusElement.innerHTML = '🟢 Connected to VANIE';
            } else {
                statusElement.className = 'connection-status disconnected';
                statusElement.innerHTML = '🔴 Disconnected from VANIE';
            }
        }
    }
    
    // Typing effect for messages
    typeMessage(element, text, speed = 50) {
        let index = 0;
        element.textContent = '';
        
        function type() {
            if (index < text.length) {
                element.textContent += text.charAt(index);
                index++;
                setTimeout(type, speed);
            }
        }
        
        type();
    }
}

// CSS for advanced features
const advancedCSS = `
<style>
/* Typing Indicators */
.typing-dots {
    display: inline-flex;
    gap: 4px;
    margin-right: 8px;
}

.typing-dots span {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: #007bff;
    animation: typing 1.4s infinite;
}

.typing-dots span:nth-child(2) {
    animation-delay: 0.2s;
}

.typing-dots span:nth-child(3) {
    animation-delay: 0.4s;
}

.typing-dots-small {
    display: inline-flex;
    gap: 2px;
    margin-left: 8px;
}

.typing-dots-small span {
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background-color: #666;
    animation: typing 1.4s infinite;
}

.typing-dots-small span:nth-child(2) {
    animation-delay: 0.2s;
}

.typing-dots-small span:nth-child(3) {
    animation-delay: 0.4s;
}

@keyframes typing {
    0%, 60%, 100% {
        transform: translateY(0);
        opacity: 0.3;
    }
    30% {
        transform: translateY(-10px);
        opacity: 1;
    }
}

/* Message Styling */
.message {
    margin: 10px 0;
    padding: 12px 16px;
    border-radius: 18px;
    max-width: 80%;
    word-wrap: break-word;
    position: relative;
}

.message.user {
    background-color: #007bff;
    color: white;
    margin-left: auto;
    text-align: right;
}

.message.bot {
    background-color: #f1f3f4;
    color: #333;
    margin-right: auto;
}

.message-content {
    margin-bottom: 4px;
}

.message-time {
    font-size: 11px;
    color: #666;
    margin-top: 4px;
}

.message.user .message-time {
    color: rgba(255, 255, 255, 0.7);
    text-align: right;
}

/* Emotion Indicators */
.emotion-indicator {
    font-size: 20px;
    margin-right: 8px;
    vertical-align: middle;
}

.emotion-notification {
    position: fixed;
    top: 20px;
    right: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 12px 20px;
    border-radius: 25px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    z-index: 1000;
    animation: slideIn 0.3s ease-out;
}

.emotion-notification.happy {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.emotion-notification.sad {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.emotion-notification.angry {
    background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.emotion-notification.excited {
    background: linear-gradient(135deg, #30cfd0 0%, #330867 100%);
}

@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

/* Connection Status */
.connection-status {
    position: fixed;
    top: 10px;
    left: 10px;
    padding: 8px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: bold;
    z-index: 1000;
}

.connection-status.connected {
    background-color: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}

.connection-status.disconnected {
    background-color: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}

/* Message Meta */
.message-meta {
    display: flex;
    gap: 8px;
    margin-top: 8px;
    font-size: 11px;
    opacity: 0.7;
}

.category-tag {
    background-color: #e9ecef;
    padding: 2px 6px;
    border-radius: 10px;
    font-weight: bold;
}

.confidence-score {
    background-color: #fff3cd;
    padding: 2px 6px;
    border-radius: 10px;
    color: #856404;
}

/* Error Notifications */
.error-notification {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background-color: #f8d7da;
    color: #721c24;
    padding: 12px 20px;
    border-radius: 8px;
    border: 1px solid #f5c6cb;
    z-index: 1000;
    animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
    from {
        transform: translateY(100%);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}

/* Typing Message */
.typing-message {
    background-color: #e9ecef;
    border: 1px dashed #adb5bd;
}

.typing-text {
    color: #6c757d;
    font-style: italic;
}
</style>
`;

// Initialize VANIE Frontend
const vanieFrontend = new VANIEFrontend();

// Add CSS to page
document.head.insertAdjacentHTML('beforeend', advancedCSS);

// Check backend health on page load
document.addEventListener('DOMContentLoaded', function() {
    vanieFrontend.checkBackendHealth();
    
    // Check health every 30 seconds
    setInterval(() => {
        vanieFrontend.checkBackendHealth();
    }, 30000);
});

// Example usage in your HTML:
// Replace your existing generateResponse function with this:

async function generateResponse(userInput) {
    try {
        // Show user message
        addMessage(userInput, 'user');
        
        // Get response from VANIE
        const response = await vanieFrontend.sendMessage(userInput);
        
        // Response is automatically displayed by the frontend
        return response;
        
    } catch (error) {
        console.error('Error in generateResponse:', error);
        // Fallback response
        addMessage("I'm having trouble connecting right now. Please try again in a moment.", 'bot');
    }
}

// Helper function to add messages (if you don't have it)
function addMessage(text, sender) {
    const chatContainer = document.getElementById('chatContainer');
    if (!chatContainer) return;
    
    const messageElement = document.createElement('div');
    messageElement.className = `message ${sender}`;
    messageElement.innerHTML = `
        <div class="message-content">${text}</div>
        <div class="message-time">${new Date().toLocaleTimeString()}</div>
    `;
    
    chatContainer.appendChild(messageElement);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Export for use in your existing code
window.VANIEFrontend = VANIEFrontend;
window.vanieFrontend = vanieFrontend;
