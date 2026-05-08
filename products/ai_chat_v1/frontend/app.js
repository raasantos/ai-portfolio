let conversationId = null;

const form = document.getElementById('input-form');
const input = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const messagesEl = document.getElementById('messages');

form.addEventListener('submit', async (e) => {
  e.preventDefault();

  const message = input.value.trim();
  if (!message) return;

  input.value = '';
  setInputEnabled(false);

  appendMessage('user', message);
  const assistantBubble = appendMessage('assistant', '');
  assistantBubble.classList.add('streaming');

  try {
    await streamResponse(message, assistantBubble);
  } catch (err) {
    assistantBubble.textContent = 'Error: could not reach the server.';
  } finally {
    assistantBubble.classList.remove('streaming');
    setInputEnabled(true);
    input.focus();
  }
});

async function streamResponse(message, bubble) {
  const response = await fetch('/chat/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, conversation_id: conversationId }),
  });

  if (!response.ok) {
    throw new Error(`Server error: ${response.status}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    const lines = buffer.split('\n');
    buffer = lines.pop(); // keep incomplete last line in buffer

    for (const line of lines) {
      if (!line.startsWith('data: ')) continue;

      const event = JSON.parse(line.slice(6));

      if (event.done) {
        conversationId = event.conversation_id;
      } else {
        bubble.textContent += event.token;
        scrollToBottom();
      }
    }
  }
}

function appendMessage(role, text) {
  const bubble = document.createElement('div');
  bubble.classList.add('message', role);
  bubble.textContent = text;
  messagesEl.appendChild(bubble);
  scrollToBottom();
  return bubble;
}

function scrollToBottom() {
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function setInputEnabled(enabled) {
  input.disabled = !enabled;
  sendBtn.disabled = !enabled;
}
