# VANIE Frontend Integration - Enhanced Algorithm
# Replace HTML JavaScript with this enhanced version

# Step 1: Remove existing generateResponse function completely
# Step 2: Add all these enhanced functions to your VANIE.html

# Enhanced generateResponse Function - Replace the existing one completely
async generateResponse(userInput) {
    try {
        // Show typing indicator
        this.showTyping();
        
        // Call Enhanced Python Backend API
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
            // Enhanced logging for debugging
            console.log('🚀 Enhanced AI Response:', {
                response: data.response,
                category: data.category,
                confidence: data.confidence,
                matched_keywords: data.matched_keywords,
                complexity_score: data.complexity_score,
                word_count: data.word_count,
                has_multiple_keywords: data.has_multiple_keywords,
                context_length: data.context_length
            });
            
            // Show category indicator
            if (data.category) {
                this.showNotification(`🎯 ${data.category.toUpperCase()} - Confidence: ${Math.round(data.confidence * 100)}%`, 'info', 2000);
            }
            
            return data.response;
        } else {
            console.error('Backend error:', data.error);
            this.showNotification('Backend error: ' + data.error, 'error');
            return this.getRandomResponse(this.responses.fallback);
        }
    } catch (error) {
        console.error('Network error:', error);
        this.hideTyping();
        
        // Enhanced error handling
        if (error.message.includes('Failed to fetch')) {
            this.showNotification('🔴 Enhanced Backend not available. Using fallback responses. ⚠️', 'error');
        }
        
        // Fallback to existing responses if backend is unavailable
        return this.getRandomResponse(this.responses.fallback);
    }
}

# Enhanced Backend Status Check with more details
async checkBackendStatus() {
    try {
        const response = await fetch('http://localhost:5000/api/health');
        const data = await response.json();
        
        if (data.status === 'healthy') {
            console.log('🚀 Enhanced Backend Connected:', data);
            
            // Show detailed connection info
            const features = data.features || {};
            const featureList = Object.keys(features).filter(f => features[f]).join(', ');
            
            this.showNotification(
                `🤖 Enhanced VANIE AI Connected! Features: ${featureList}`, 
                'success', 
                4000
            );
            
            // Update status indicator with enhanced styling
            const statusDot = document.querySelector('.status-dot');
            if (statusDot) {
                statusDot.style.background = 'rgba(0, 255, 0, 0.8)';
                statusDot.style.boxShadow = '0 0 8px rgba(0, 255, 0, 0.4)';
            }
            
            // Update bot status text
            const statusText = document.getElementById('statusText');
            if (statusText) {
                statusText.textContent = 'Enhanced AI Active';
            }
            
            return true;
        }
    } catch (error) {
        console.error('Enhanced Backend connection failed:', error);
        this.showNotification('🔴 Enhanced Backend not available. Using advanced fallback responses. ⚠️', 'error');
        
        // Update status indicator
        const statusDot = document.querySelector('.status-dot');
        if (statusDot) {
            statusDot.style.background = 'rgba(255, 59, 48, 0.8)';
            statusDot.style.boxShadow = '0 0 8px rgba(255, 59, 48, 0.4)';
        }
        
        return false;
    }
}

# Enhanced init function with backend check
async init() {
    this.loadSettings();
    this.loadChatHistory();
    this.initVoiceRecognition();
    this.setupEventListeners();
    
    // Check enhanced backend connection first
    const backendAvailable = await this.checkBackendStatus();
    
    if (backendAvailable) {
        console.log('🚀 VANIE is running with Enhanced Python Backend AI!');
        this.showNotification('🤖 Enhanced AI Features Active: Multi-keyword detection, Context awareness, Complexity analysis', 'success', 3000);
    } else {
        console.log('⚠️ VANIE is running with fallback responses only.');
        this.showNotification('⚠️ Running in fallback mode. Start enhanced backend for full features!', 'error', 3000);
    }
    
    this.sendInitialMessage();
}

# New function to get conversation statistics
async getConversationStats() {
    try {
        const response = await fetch(`http://localhost:5000/api/stats?session_id=${this.state.userId || 'default'}`);
        const data = await response.json();
        
        if (data.status === 'success') {
            console.log('📊 Conversation Stats:', data.stats);
            
            const stats = data.stats;
            const statsMessage = `
                📊 Conversation Statistics:
                💬 Total Messages: ${stats.total_messages}
                🎯 Categories: ${stats.categories_discussed.join(', ')}
                🧠 Avg Complexity: ${stats.avg_complexity}
                ⏱️ Session Duration: ${stats.session_duration}
            `;
            
            this.showNotification(statsMessage, 'info', 6000);
        }
    } catch (error) {
        console.error('Error getting stats:', error);
    }
}

# Enhanced function to clear conversation with confirmation
async clearEnhancedConversation() {
    if (confirm('Are you sure you want to clear the entire conversation history? This will reset all context and learning.')) {
        try {
            const response = await fetch(`http://localhost:5000/api/clear?session_id=${this.state.userId || 'default'}`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.showNotification('🗑️ Enhanced conversation context cleared successfully!', 'success');
                this.clearChat();
            }
        } catch (error) {
            console.error('Error clearing conversation:', error);
            this.showNotification('Error clearing conversation', 'error');
        }
    }
}

# Add keyboard shortcut for stats
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        // Call getConversationStats if it exists in VANIE object
        if (window.VANIE && window.VANIE.getConversationStats) {
            window.VANIE.getConversationStats();
        }
    }
});

# Enhanced CSS for backend status
const enhancedCSS = `
.backend-status-indicator {
    display: inline-flex;
    align-items: center;
    gap: 12px;
    margin-left: 12px;
    padding: 6px 12px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.backend-status-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.4);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
}

.backend-status-dot.connected {
    background: linear-gradient(45deg, #00ff88, #00cc66);
    box-shadow: 0 0 12px rgba(0, 255, 136, 0.4);
    animation: pulse-green 2s infinite;
}

.backend-status-dot.disconnected {
    background: linear-gradient(45deg, #ff4444, #cc0000);
    box-shadow: 0 0 12px rgba(255, 68, 68, 0.4);
    animation: pulse-red 2s infinite;
}

.backend-status-text {
    font-size: 12px;
    color: var(--text-secondary);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

@keyframes pulse-green {
    0%, 100% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.2); opacity: 0.8; }
}

@keyframes pulse-red {
    0%, 100% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.2); opacity: 0.8; }
}

.enhanced-ai-badge {
    background: linear-gradient(45deg, #667eea, #764ba2);
    color: white;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 10px;
    font-weight: 600;
    margin-left: 8px;
    animation: shimmer 3s infinite;
}

@keyframes shimmer {
    0% { background-position: -200% center; }
    100% { background-position: 200% center; }
}
`;

# Add this CSS to your document head
const styleElement = document.createElement('style');
styleElement.textContent = enhancedCSS;
document.head.appendChild(styleElement);

# Enhanced HTML for status indicator
# Update your bot-status div in HTML to:
<div class="bot-status">
    <span class="backend-status-indicator">
        <span class="backend-status-dot" id="backendStatusDot"></span>
        <span class="backend-status-text" id="backendStatusText">Initializing...</span>
        <span class="enhanced-ai-badge" id="enhancedAIBadge" style="display: none;">ENHANCED AI</span>
    </span>
    <span id="statusText">Online</span>
</div>

# Show enhanced AI badge when backend is connected
function showEnhancedAIBadge() {
    const badge = document.getElementById('enhancedAIBadge');
    if (badge) {
        badge.style.display = 'inline-block';
    }
}

# Add stats button to header actions
# Add this HTML to your header actions section:
<button class="icon-btn" id="statsBtn" title="Conversation Stats (Ctrl+S)">
    <i class="fas fa-chart-bar"></i>
</button>

# Add event listener for stats button
# Add to your setupEventListeners function:
document.getElementById('statsBtn').addEventListener('click', () => {
    if (window.VANIE && window.VANIE.getConversationStats) {
        window.VANIE.getConversationStats();
    }
});

# Enhanced notification system for backend events
function showBackendNotification(message, type = 'info', duration = 4000) {
    const container = document.getElementById('notificationContainer');
    if (!container) return;
    
    const notification = document.createElement('div');
    notification.className = `in-app-notification ${type}`;
    
    let icon = 'fas fa-info-circle';
    if (type === 'success') icon = 'fas fa-check-circle';
    else if (type === 'error') icon = 'fas fa-exclamation-circle';
    else if (type === 'warning') icon = 'fas fa-exclamation-triangle';
    
    notification.innerHTML = `
        <div class="notification-content">
            <div class="notification-icon">
                <i class="${icon}"></i>
            </div>
            <div class="notification-text">${message}</div>
        </div>
        <button class="notification-close">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    container.appendChild(notification);
    
    // Show animation
    setTimeout(() => {
        notification.classList.add('show');
    }, 50);
    
    // Auto-remove with enhanced animation
    setTimeout(() => {
        notification.classList.add('hide');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, duration);
}
