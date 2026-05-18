const chatContainer = document.getElementById('chat-container');
const queryInput = document.getElementById('query-input');
const sendBtn = document.getElementById('send-btn');
const langSelect = document.getElementById('language-select');
const statusBadge = document.getElementById('connection-status');

// Handle Textarea Auto-resize
queryInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
});

// Allow Enter key to send
queryInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendQuery();
    }
});

sendBtn.addEventListener('click', sendQuery);

// Allow clicking chips to pre-fill and send
window.setQuery = function(text) {
    queryInput.value = text;
    sendQuery();
}

function appendMessage(text, sender, isRetrieved = false) {
    // Hide welcome message if it's the first chat
    const welcome = document.querySelector('.welcome-message');
    if (welcome) welcome.style.display = 'none';

    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}`;
    
    if (sender === 'ai' && isRetrieved) {
        const badge = document.createElement('div');
        badge.className = 'retrieval-badge';
        badge.innerHTML = '<i class="fa-solid fa-check-circle"></i> Source: Vetted Guidelines';
        msgDiv.appendChild(badge);
    }
    
    const textSpan = document.createElement('div');
    textSpan.innerText = text;
    msgDiv.appendChild(textSpan);
    
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    typingDiv.id = 'typing-indicator';
    typingDiv.innerHTML = `
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    `;
    chatContainer.appendChild(typingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function removeTypingIndicator() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

async function sendQuery() {
    const query = queryInput.value.trim();
    if (!query) return;

    // Reset input
    queryInput.value = '';
    queryInput.style.height = 'auto';

    // Show user message
    appendMessage(query, 'user');

    // Show typing indicator
    showTypingIndicator();

    const language = langSelect.value;

    try {
        const response = await fetch('http://127.0.0.1:5000/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query, language })
        });

        const data = await response.json();
        removeTypingIndicator();
        
        if (response.ok) {
            appendMessage(data.answer, 'ai', data.retrieved_context);
        } else {
            appendMessage(`Error: ${data.error || 'Failed to get response'}`, 'ai');
        }
    } catch (err) {
        removeTypingIndicator();
        appendMessage('Connection Error: Unable to reach the local SehatMitra engine. Please ensure the backend is running.', 'ai');
        console.error(err);
    }
}

// Simple periodic check to see if backend is running
setInterval(async () => {
    try {
        const res = await fetch('http://127.0.0.1:5000/health');
        if (res.ok) {
            statusBadge.className = 'status-badge';
            statusBadge.style.color = 'var(--secondary)';
            statusBadge.style.borderColor = 'rgba(16, 185, 129, 0.3)';
            statusBadge.style.background = 'rgba(16, 185, 129, 0.2)';
            statusBadge.innerHTML = '<i class="fa-solid fa-wifi"></i> Online (Local AI)';
        }
    } catch (e) {
        statusBadge.className = 'status-badge offline';
        statusBadge.style.color = '#ef4444';
        statusBadge.style.borderColor = 'rgba(239, 68, 68, 0.3)';
        statusBadge.style.background = 'rgba(239, 68, 68, 0.1)';
        statusBadge.innerHTML = '<i class="fa-solid fa-plane"></i> Offline Engine';
    }
}, 5000);
