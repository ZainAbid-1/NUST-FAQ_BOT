const form = document.getElementById('chatForm');
const input = document.getElementById('userInput');
const btn = document.getElementById('sendBtn');
const chatContainer = document.getElementById('chatContainer');

// Scroll down helper
const scrollToBottom = () => {
    chatContainer.scrollTop = chatContainer.scrollHeight;
};

// Create typing indicator element
const createTypingIndicator = () => {
    const row = document.createElement('div');
    row.className = 'message-row ai-row';
    row.id = 'typingIndicator';
    row.innerHTML = `
        <div class="message ai-message">
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
    `;
    return row;
};

// Render citations
const formatCitations = (citations) => {
    if (!citations || citations.length === 0) return '';
    
    // Deduplicate
    const unique = [];
    const map = new Map();
    for(const item of citations) {
        if(!map.has(item.question)){
            map.set(item.question, true);
            unique.push(item);
        }
    }
    
    const chips = unique.map(c => `<div class="citation-chip" title="${c.question}">${c.category} - Source</div>`).join('');
    return `<div class="citations-box">${chips}</div>`;
};

let chatHistory = [];

// Handle submission
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = input.value.trim();
    if (!query) return;

    // 1. Add User Message
    const userRow = document.createElement('div');
    userRow.className = 'message-row user-row';
    userRow.innerHTML = `<div class="message user-message"><p>${query}</p></div>`;
    chatContainer.appendChild(userRow);
    
    input.value = '';
    btn.disabled = true;
    scrollToBottom();

    // 2. Add Typing Indicator
    const typingRow = createTypingIndicator();
    chatContainer.appendChild(typingRow);
    scrollToBottom();

    try {
        // 3. Request API
        const d_start = performance.now();
        const response = await fetch('/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, history: chatHistory })
        });
        
        const data = await response.json();
        const d_end = performance.now();
        const latency = ((d_end - d_start) / 1000).toFixed(2);
        
        // Push user query and AI response to history
        chatHistory.push({ role: 'user', content: query });
        chatHistory.push({ role: 'assistant', content: data.answer });
        
        // Keep history size manageable (e.g., last 6 messages)
        if (chatHistory.length > 6) {
            chatHistory = chatHistory.slice(chatHistory.length - 6);
        }
        
        // Remove typing indicator
        document.getElementById('typingIndicator').remove();

        // 4. Extract Confidence
        let confColor = data.confidence_status || "green";
        let confText = confColor === "green" ? "High Confidence" : "Low Confidence (Fallback Triggered)";

        let confidenceDOM = `
            <div class="confidence-indicator">
                <div class="dot ${confColor}"></div>
                <span>${confText} (${latency}s)</span>
            </div>
        `;

        // 5. Append AI message
        const aiRow = document.createElement('div');
        aiRow.className = 'message-row ai-row';
        
        let answerParsed = data.answer.replace(/\n/g, "<br>");
        
        aiRow.innerHTML = `
            <div class="message ai-message">
                ${confidenceDOM}
                <p>${answerParsed}</p>
                ${formatCitations(data.citations)}
            </div>
        `;
        chatContainer.appendChild(aiRow);

    } catch (err) {
        document.getElementById('typingIndicator').remove();
        const errorRow = document.createElement('div');
        errorRow.className = 'message-row ai-row';
        errorRow.innerHTML = `<div class="message ai-message"><p style="color:var(--confidence-red)">Connection Error: The offline engine is currently unreachable. Please ensure the backend is running.</p></div>`;
        chatContainer.appendChild(errorRow);
    } finally {
        btn.disabled = false;
        scrollToBottom();
        input.focus();
    }
});
