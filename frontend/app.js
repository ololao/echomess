document.addEventListener('DOMContentLoaded', () => {
  let ws = null;
  let currentUser = '';
  let currentRoom = '';
  let autoReconnectTimer = null;

  // DOM Elements
  const joinScreen = document.getElementById('join-screen');
  const chatScreen = document.getElementById('chat-screen');
  const joinForm = document.getElementById('join-form');
  const messageForm = document.getElementById('message-form');
  const usernameInput = document.getElementById('username');
  const roomIdInput = document.getElementById('room-id');
  const messageInput = document.getElementById('message-input');
  const messageContainer = document.getElementById('message-container');
  const currentRoomTitle = document.getElementById('current-room-title');
  const welcomeRoomName = document.getElementById('welcome-room-name');
  const statusDot = document.getElementById('status-dot');
  const statusText = document.getElementById('status-text');
  const leaveBtn = document.getElementById('leave-btn');
  const chipBtns = document.querySelectorAll('.chip-btn');

  // Quick room chips
  chipBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      roomIdInput.value = btn.dataset.room;
    });
  });

  // Handle joining room
  joinForm.addEventListener('submit', (e) => {
    e.preventDefault();
    currentUser = usernameInput.value.trim() || 'Anonymous';
    currentRoom = roomIdInput.value.trim().toLowerCase().replace(/[^a-z0-9_-]/g, '') || 'general';

    if (!currentRoom) return;

    joinScreen.classList.remove('active');
    chatScreen.classList.add('active');
    currentRoomTitle.textContent = `#${currentRoom}`;
    welcomeRoomName.textContent = `#${currentRoom}`;

    connectWebSocket();
  });

  // Handle leaving room
  leaveBtn.addEventListener('click', () => {
    if (ws) {
      ws.close();
    }
    clearTimeout(autoReconnectTimer);
    chatScreen.classList.remove('active');
    joinScreen.classList.add('active');
    messageContainer.innerHTML = `
      <div class="welcome-message">
        <p>👋 Welcome to room <strong id="welcome-room-name">#${currentRoom}</strong>!</p>
        <span class="subtext">Messages sent here are broadcast in real-time.</span>
      </div>
    `;
  });

  // Handle message submit
  messageForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const text = messageInput.value.trim();
    if (!text || !ws || ws.readyState !== WebSocket.OPEN) return;

    const payload = {
      sender: currentUser,
      text: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    try {
      ws.send(JSON.stringify(payload));
      messageInput.value = '';
    } catch (err) {
      console.error('Failed to send message:', err);
    }
  });

  // Connect to WebSocket
  function connectWebSocket() {
    updateStatus('connecting', 'Connecting...');

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const roomParam = encodeURIComponent(currentRoom);

    const directUrl = `${protocol}//${window.location.hostname}:8000/${currentRoom}?room_id=${roomParam}`;
    const proxyUrl = `${protocol}//${window.location.host}/${currentRoom}?room_id=${roomParam}`;

    console.log(`Attempting WebSocket connection to: ${directUrl}`);

    function setupSocket(url, fallbackUrl) {
      try {
        ws = new WebSocket(url);
      } catch (err) {
        if (fallbackUrl) {
          return setupSocket(fallbackUrl, null);
        }
        return;
      }

      let connected = false;

      ws.onopen = () => {
        connected = true;
        updateStatus('connected', 'Connected');
        addSystemMessage(`Connected to #${currentRoom}`);
      };

      ws.onmessage = (event) => {
        try {
          let data = event.data;
          if (typeof data === 'string') {
            try { data = JSON.parse(data); } catch (e) {}
          }
          if (typeof data === 'string') {
            try { data = JSON.parse(data); } catch (e) {}
          }
          renderMessage(data);
        } catch (err) {
          console.error('Error handling WS message:', err);
        }
      };

      ws.onerror = (err) => {
        console.error(`WebSocket Error on ${url}:`, err);
        if (!connected && fallbackUrl) {
          console.log(`Fallback connection to: ${fallbackUrl}`);
          ws.close();
          setupSocket(fallbackUrl, null);
        } else {
          updateStatus('disconnected', 'Connection Error');
        }
      };

      ws.onclose = (event) => {
        if (connected) {
          updateStatus('disconnected', 'Disconnected');
          if (chatScreen.classList.contains('active')) {
            addSystemMessage('Connection lost. Reconnecting in 3 seconds...');
            clearTimeout(autoReconnectTimer);
            autoReconnectTimer = setTimeout(() => {
              connectWebSocket();
            }, 3000);
          }
        }
      };
    }

    setupSocket(directUrl, proxyUrl);
  }


  function updateStatus(state, text) {
    statusText.textContent = text;
    statusDot.className = `dot ${state === 'connected' ? 'connected' : 'disconnected'}`;
  }

  function addSystemMessage(text) {
    const sysDiv = document.createElement('div');
    sysDiv.className = 'system-msg';
    sysDiv.textContent = text;
    messageContainer.appendChild(sysDiv);
    scrollToBottom();
  }

  function renderMessage(data) {
    const sender = data.sender || 'Anonymous';
    const text = data.text || (typeof data === 'string' ? data : JSON.stringify(data));
    const timestamp = data.timestamp || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const isSelf = sender === currentUser;

    const wrapper = document.createElement('div');
    wrapper.className = `msg-wrapper ${isSelf ? 'self' : 'other'}`;

    const meta = document.createElement('div');
    meta.className = 'msg-meta';
    meta.textContent = isSelf ? timestamp : `${sender} • ${timestamp}`;

    const bubble = document.createElement('div');
    bubble.className = 'msg-bubble';
    bubble.textContent = text;

    wrapper.appendChild(meta);
    wrapper.appendChild(bubble);

    messageContainer.appendChild(wrapper);
    scrollToBottom();
  }

  function scrollToBottom() {
    messageContainer.scrollTop = messageContainer.scrollHeight;
  }
});
