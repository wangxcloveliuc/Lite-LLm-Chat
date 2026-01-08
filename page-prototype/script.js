// DOM Elements
const newChatBtn = document.getElementById('newChatBtn');
const modelSelectors = document.querySelectorAll('.model-selector');
const textInput = document.getElementById('textInput');
const attachmentBtn = document.getElementById('attachmentBtn');
const sendBtn = document.getElementById('sendBtn');
const providerDropdown = document.getElementById('providerDropdown');
const chatMessages = document.getElementById('chatMessages');
const greeting = document.getElementById('greeting');
const inputContainer = document.querySelector('.input-container');

// State Management
let isRecording = false;
let isVoiceMode = false;
let currentModel = 'gpt-3.5-turbo';
let currentProvider = 'Doubao';
let isChatActive = false;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    setupKeyboardShortcuts();
});

// Event Listeners
function initializeEventListeners() {
    // Sidebar buttons
    newChatBtn.addEventListener('click', handleNewChat);
    
    // Model selectors
    modelSelectors.forEach((selector, index) => {
        selector.addEventListener('click', (e) => handleSelectorClick(e, index));
    });
    
    // Input functionality
    textInput.addEventListener('input', handleTextInput);
    textInput.addEventListener('keydown', handleInputKeydown);
    
    // Action buttons
    attachmentBtn.addEventListener('click', handleAttachment);
    sendBtn.addEventListener('click', handleSendMessage);
    
    // Focus management
    textInput.addEventListener('focus', () => {
        document.querySelector('.input-bar').classList.add('focused');
    });
    
    textInput.addEventListener('blur', () => {
        document.querySelector('.input-bar').classList.remove('focused');
    });
}

// Keyboard Shortcuts
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + N for new chat
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            e.preventDefault();
            handleNewChat();
        }
        
        // Escape to clear input
        if (e.key === 'Escape' && document.activeElement === textInput) {
            textInput.value = '';
            textInput.blur();
        }
    });
}

// Handler Functions
function handleNewChat() {
    console.log('New chat initiated');
    deactivateChatMode();
    textInput.focus();
    
    // Add animation
    document.querySelector('.central-interface').classList.add('fade-in');
    setTimeout(() => {
        document.querySelector('.central-interface').classList.remove('fade-in');
    }, 300);
}


function handleSelectorClick(e, selectorIndex) {
    const selector = e.currentTarget;
    const selectorText = selector.querySelector('span').textContent;
    
    // Add rotation animation to chevron
    const chevron = selector.querySelector('.chevron-icon');
    chevron.style.transform = 'rotate(180deg)';
    setTimeout(() => {
        chevron.style.transform = '';
    }, 200);
    
    if (selectorText === 'Provider') {
        showProviderDropdown(selector);
    } else if (selectorText === 'Model') {
        const models = ['gpt-3.5-turbo', 'gpt-4', 'claude-3', 'gemini-pro'];
        const currentIndex = models.indexOf(currentModel);
        const nextIndex = (currentIndex + 1) % models.length;
        currentModel = models[nextIndex];
        
        console.log('Model changed to:', currentModel);
    }
}

// Provider Dropdown Functions
function showProviderDropdown(triggerElement) {
    const rect = triggerElement.getBoundingClientRect();
    const dropdownContainer = providerDropdown.querySelector('.dropdown-container');
    
    // Position dropdown below the trigger element
    dropdownContainer.style.top = `${rect.bottom + 8}px`;
    dropdownContainer.style.left = `${rect.left}px`;
    
    providerDropdown.classList.add('show');
    
    // Add event listeners for provider options
    const providerOptions = document.querySelectorAll('.provider-option');
    providerOptions.forEach(option => {
        option.addEventListener('click', handleProviderSelection);
    });
    
    // Close dropdown when clicking outside
    providerDropdown.addEventListener('click', (e) => {
        if (e.target === providerDropdown) {
            hideProviderDropdown();
        }
    });
}

function hideProviderDropdown() {
    providerDropdown.classList.remove('show');
}

function handleProviderSelection(e) {
    const selectedOption = e.currentTarget;
    const providerName = selectedOption.dataset.provider;
    
    // Update selected state
    document.querySelectorAll('.provider-option').forEach(option => {
        option.classList.remove('selected');
        const checkmark = option.querySelector('.checkmark');
        if (checkmark) {
            checkmark.remove();
        }
    });
    
    selectedOption.classList.add('selected');
    
    // Add checkmark to selected option
    const checkmark = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    checkmark.setAttribute('class', 'checkmark');
    checkmark.setAttribute('viewBox', '0 0 24 24');
    checkmark.setAttribute('fill', 'none');
    checkmark.setAttribute('stroke', 'currentColor');
    checkmark.setAttribute('stroke-width', '2');
    checkmark.innerHTML = '<path d="M20 6L9 17l-5-5"/>';
    selectedOption.appendChild(checkmark);
    
    // Update current provider
    currentProvider = providerName.charAt(0).toUpperCase() + providerName.slice(1);
    
    console.log('Provider changed to:', currentProvider);
    
    // Hide dropdown
    setTimeout(() => {
        hideProviderDropdown();
    }, 150);
}

function handleTextInput(e) {
    const value = e.target.value.trim();
    
    // Enable/disable send button based on content
    if (value.length > 0) {
        sendBtn.style.backgroundColor = '#3B82F6';
    } else {
        sendBtn.style.backgroundColor = '#000000';
    }
}

function handleInputKeydown(e) {
    const value = e.target.value.trim();
    
    // Enter to send (without Shift)
    if (e.key === 'Enter' && !e.shiftKey && value.length > 0) {
        e.preventDefault();
        sendMessage(value);
    }
    
    // Shift + Enter for new line
    if (e.key === 'Enter' && e.shiftKey) {
        // Allow default behavior (new line)
    }
}

function handleAttachment() {
    console.log('Attachment clicked');
    // Create file input
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = 'image/*,.pdf,.doc,.docx,.txt';
    fileInput.onchange = (e) => {
        const file = e.target.files[0];
        if (file) {
            console.log('File selected:', file.name);
        }
    };
    fileInput.click();
}

function handleSendMessage() {
    const value = textInput.value.trim();
    
    if (value.length > 0) {
        if (!isChatActive) {
            activateChatMode();
        }
        sendMessage(value);
    } else {
        console.log('Please enter a message to send');
    }
}

function activateChatMode() {
    isChatActive = true;
    greeting.classList.add('hidden');
    chatMessages.classList.add('visible');
    inputContainer.classList.add('chat-active');
}

function deactivateChatMode() {
    isChatActive = false;
    greeting.classList.remove('hidden');
    chatMessages.classList.remove('visible');
    inputContainer.classList.remove('chat-active');
    chatMessages.innerHTML = '';
}

// Voice Recording Functions
function startRecording() {
    console.log('Recording started');
    micBtn.style.backgroundColor = '#EF4444';
    micBtn.querySelector('.icon').style.color = '#FFFFFF';
    
    // Simulate recording (in real app, you'd use Web Audio API)
    setTimeout(() => {
        if (isRecording) {
            stopRecording();
        }
    }, 5000);
}

function stopRecording() {
    console.log('Recording stopped');
    isRecording = false;
    micBtn.style.backgroundColor = '';
    micBtn.querySelector('.icon').style.color = '#6B7280';
}

// Voice Mode Functions
function startVoiceMode() {
    console.log('Voice mode activated');
    voiceModeBtn.style.backgroundColor = '#10B981';
    
    // Simulate voice recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'zh-CN';
        
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            textInput.value = transcript;
            console.log(`Recognized: ${transcript}`);
        };
        
        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
        };
        
        recognition.start();
    } else {
        console.log('Browser does not support speech recognition');
    }
}

function stopVoiceMode() {
    console.log('Voice mode deactivated');
    isVoiceMode = false;
    voiceModeBtn.style.backgroundColor = '#000000';
}

// Message Sending
function sendMessage(message) {
    console.log('Sending message:', message);
    
    // Add user message to chat
    addMessageToChat(message, 'user');
    
    // Clear input
    textInput.value = '';
    
    // Show loading state
    sendBtn.style.backgroundColor = '#F59E0B';
    sendBtn.innerHTML = `
        <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
            <circle cx="12" cy="12" r="10" opacity="0.3"/>
            <path d="M12 2v10l4 4" stroke="currentColor" stroke-width="2" fill="none"/>
        </svg>
    `;
    
    // Simulate API response
    setTimeout(() => {
        const response = generateResponse(message);
        addMessageToChat(response, 'assistant');
        
        // Reset send button
        sendBtn.innerHTML = `
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
            </svg>
        `;
        sendBtn.style.backgroundColor = '#000000';
    }, 1500);
}

function addMessageToChat(message, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    messageDiv.textContent = message;
    
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function generateResponse(userMessage) {
    const responses = [
        'I understand your question. Let me help you with that.',
        'That\'s an interesting point. Here\'s what I think...',
        'Based on what you\'ve told me, I would suggest...',
        'I can definitely assist you with this. Let me explain...',
        'Great question! Here\'s my perspective on that...'
    ];
    
    return responses[Math.floor(Math.random() * responses.length)];
}

// Utility Functions
function showNotification(message) {
    // Create notification element
    const notification = document.createElement('div');
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        background-color: #1F2937;
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        font-size: 14px;
        z-index: 1000;
        opacity: 0;
        transition: opacity 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Show notification
    setTimeout(() => {
        notification.style.opacity = '1';
    }, 10);
    
    // Hide and remove after 3 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Auto-resize textarea (if you change input to textarea)
function autoResize(element) {
    element.style.height = 'auto';
    element.style.height = element.scrollHeight + 'px';
}

// Initialize tooltips (optional enhancement)
function initializeTooltips() {
    const tooltipData = {
        'newChatBtn': 'Start new chat (Ctrl+N)',
        'attachmentBtn': 'Add attachment',
        'sendBtn': 'Send message'
    };
    
    Object.entries(tooltipData).forEach(([id, text]) => {
        const element = document.getElementById(id);
        if (element) {
            element.title = text;
        }
    });
}

// Call tooltip initialization
initializeTooltips();
