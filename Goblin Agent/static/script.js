function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

function addMessage(text, isUser) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user' : 'agent'}`;

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.textContent = text;

    messageDiv.appendChild(bubble);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addLoadingIndicator() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message agent';
    messageDiv.id = 'loading-indicator';

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble loading';

    for (let i = 0; i < 3; i++) {
        const dot = document.createElement('div');
        dot.className = 'loading-dot';
        bubble.appendChild(dot);
    }

    messageDiv.appendChild(bubble);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeLoadingIndicator() {
    const loadingIndicator = document.getElementById('loading-indicator');
    if (loadingIndicator) {
        loadingIndicator.remove();
    }
}

async function sendMessage() {
    const message = messageInput.value.trim();

    if (!message) {
        return;
    }

    addMessage(message, true);
    messageInput.value = '';
    sendButton.disabled = true;
    messageInput.disabled = true;

    addLoadingIndicator();

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message }),
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        removeLoadingIndicator();
        addMessage(data.reply, false);
    } catch (error) {
        removeLoadingIndicator();
        addMessage('Sorry, something went wrong. Please try again.', false);
        console.error('Error:', error);
    } finally {
        sendButton.disabled = false;
        messageInput.disabled = false;
        messageInput.focus();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chatMessages');
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');

    sendButton.addEventListener('click', sendMessage);

    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    messageInput.focus();
});
