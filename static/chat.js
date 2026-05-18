document.addEventListener('DOMContentLoaded', () => {
    const bubble = document.getElementById('chat-bubble');
    const window = document.getElementById('chat-window');
    const closeBtn = document.getElementById('chat-close');
    const sendBtn = document.getElementById('chat-send');
    const input = document.getElementById('chat-input');
    const messagesContainer = document.getElementById('chat-messages');

    // Toggle Chat Window
    bubble.addEventListener('click', () => {
        const isVisible = window.style.display === 'flex';
        window.style.display = isVisible ? 'none' : 'flex';
        if (!isVisible) {
            input.focus();
            if (messagesContainer.children.length === 0) {
                addMessage('bot', 'Hi! I\'m Port Buddy. How can I help you with your network security today?');
            }
        }
    });

    closeBtn.addEventListener('click', () => {
        window.style.display = 'none';
    });

    // Send Message Logic
    const handleSend = async () => {
        const text = input.value.trim();
        if (!text) return;

        addMessage('user', text);
        input.value = '';
        
        // Show typing indicator
        const typingId = showTypingStatus();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });
            const data = await response.json();
            
            removeTypingStatus(typingId);
            addMessage('bot', data.response);
        } catch (error) {
            removeTypingStatus(typingId);
            addMessage('bot', 'Sorry, I\'m having trouble connecting to my brain right now. Please try again later.');
        }
    };

    sendBtn.addEventListener('click', handleSend);
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSend();
    });

    // Helper functions
    function addMessage(sender, text) {
        const div = document.createElement('div');
        div.className = `message ${sender}`;
        if (sender === 'bot') {
            div.innerHTML = typeof marked !== 'undefined' ? marked.parse(text) : text;
        } else {
            div.textContent = text;
        }
        messagesContainer.appendChild(div);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function showTypingStatus() {
        const id = 'typing-' + Date.now();
        const div = document.createElement('div');
        div.id = id;
        div.className = 'message bot typing-dots';
        div.innerHTML = '<span></span><span></span><span></span>';
        messagesContainer.appendChild(div);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        return id;
    }

    function removeTypingStatus(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }
});
