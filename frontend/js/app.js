"use strict";

/* ============================================================
   API клиент
   ============================================================ */
const API = {
  token: null,

  async _fetch(path, options = {}) {
    const headers = { ...(options.headers || {}) };
    if (this.token) headers["Authorization"] = `Bearer ${this.token}`;
    if (options.body && typeof options.body === "object") {
      headers["Content-Type"] = "application/json";
      options.body = JSON.stringify(options.body);
    }
    const res = await fetch(path, {
      ...options,
      headers,
      credentials: "same-origin",
    });

    if (res.status === 401) {
      const refreshed = await this.refresh();
      if (refreshed) {
        headers["Authorization"] = `Bearer ${this.token}`;
        const retryRes = await fetch(path, {
          ...options,
          headers,
          credentials: "same-origin",
        });
        return retryRes;
      }
    }
    return res;
  },

  async refresh() {
    try {
      const res = await fetch("/api/auth/refresh", { credentials: "same-origin" });
      if (!res.ok) return false;
      const data = await res.json();
      this.token = data.token;
      return true;
    } catch {
      return false;
    }
  },

  setToken(t) {
    this.token = t;
  },

  async register(name, email, password) {
    const res = await this._fetch("/api/auth/registry", {
      method: "POST",
      body: { name, email, password },
    });
    return API._parse(res);
  },

  async login(email, password) {
    const res = await this._fetch("/api/auth/login", {
      method: "POST",
      body: { email, password },
    });
    return API._parse(res);
  },

  async codeCallback(attemptId, code) {
    const res = await this._fetch("/api/auth/code-callback", {
      method: "POST",
      body: { attempt_id: attemptId, code },
    });
    return API._parse(res);
  },

  async urlCallback(token) {
    const res = await this._fetch(`/api/auth/url-callback?token=${encodeURIComponent(token)}`);
    return API._parse(res);
  },

  async getRooms(search = "", page = 1) {
    const q = new URLSearchParams();
    if (search) q.set("search", search);
    q.set("page_number", page);
    q.set("page_limit", 30);
    const res = await this._fetch(`/api/room/?${q}`);
    return API._parse(res);
  },

  async createRoom(name) {
    const res = await this._fetch("/api/room/", { method: "POST", body: { name } });
    return API._parse(res);
  },

  async getMessages(roomId, direction, limit, cursorIso) {
    const q = new URLSearchParams();
    q.set("direction", direction);
    q.set("limit", limit);
    q.set("cursor", cursorIso);
    const res = await this._fetch(`/api/msg/${roomId}?${q}`);
    return API._parse(res);
  },

  async _parse(res) {
    if (res.ok) {
      const text = await res.text();
      return { ok: true, data: text ? JSON.parse(text) : null };
    }
    let detail = `Ошибка ${res.status}`;
    try {
      const err = await res.json();
      if (err.detail) detail = typeof err.detail === "string" ? err.detail : JSON.stringify(err.detail);
    } catch {}
    return { ok: false, error: detail };
  },
};

/* ============================================================
   Утилиты
   ============================================================ */
const $ = (sel) => document.querySelector(sel);

function toast(msg, type = "") {
  const el = document.createElement("div");
  el.className = `toast ${type}`;
  el.textContent = msg;
  $("#toast").appendChild(el);
  setTimeout(() => el.remove(), 3500);
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

function fmtTime(iso) {
  const d = new Date(iso);
  if (isNaN(d)) return "";
  return d.toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" });
}

/* ============================================================
   Точка входа
   ============================================================ */
window.addEventListener("DOMContentLoaded", async () => {
  // Обработка ссылки подтверждения из письма: /auth/url-callback?token=...
  const params = new URLSearchParams(window.location.search);
  const cbToken = params.get("token");
  const onCallbackPath = window.location.pathname.replace(/\/$/, "").endsWith("/auth/url-callback");
  if (onCallbackPath && cbToken) {
    handleEmailCallback(cbToken);
    return;
  }

  // Пытаемся получить access-токен через refresh-куку (httpOnly)
  const refreshed = await API.refresh();
  if (refreshed) {
    enterApp();
  } else {
    showAuth();
  }
});

/* ============================================================
   Подтверждение почты по ссылке
   ============================================================ */
async function handleEmailCallback(token) {
  $("#auth").classList.add("hidden");
  $("#email-callback").classList.remove("hidden");
  const status = $("#callback-status");

  const res = await API.urlCallback(token);
  if (res.ok) {
    API.setToken(res.data.token);
    status.textContent = "Готово! Перенаправляем в чат...";
    toast("Почта подтверждена. Добро пожаловать!", "ok");
    setTimeout(() => {
      history.replaceState({}, "", "/");
      enterApp();
    }, 1200);
  } else {
    status.innerHTML = `Не удалось подтвердить почту: ${escapeHtml(res.error)}.<br>Возможно, ссылка устарела (она действует 5 минут).`;
  }
}

/* ============================================================
   Экран авторизации
   ============================================================ */
function showAuth() {
  $("#email-callback").classList.add("hidden");
  $("#app").classList.add("hidden");
  $("#auth").classList.remove("hidden");

  const tabLogin = $("#tab-login");
  const tabRegister = $("#tab-register");
  const loginForm = $("#login-form");
  const codeForm = $("#code-form");
  const registerForm = $("#register-form");

  let attemptId = null;

  function switchTab(which) {
    tabLogin.classList.toggle("active", which === "login");
    tabRegister.classList.toggle("active", which === "register");
    loginForm.classList.toggle("hidden", which !== "login");
    codeForm.classList.add("hidden");
    registerForm.classList.toggle("hidden", which !== "register");
  }
  tabLogin.onclick = () => switchTab("login");
  tabRegister.onclick = () => switchTab("register");

  // Вход: email+пароль -> отправка кода
  loginForm.onsubmit = async (e) => {
    e.preventDefault();
    const email = $("#login-email").value.trim();
    const password = $("#login-password").value;
    const btn = loginForm.querySelector("button[type=submit]");
    btn.disabled = true;
    const res = await API.login(email, password);
    btn.disabled = false;
    if (res.ok) {
      attemptId = res.data.attempt_id;
      loginForm.classList.add("hidden");
      codeForm.classList.remove("hidden");
      toast("Код отправлен на почту", "ok");
    } else {
      toast(res.error, "error");
    }
  };

  // Ввод кода
  codeForm.onsubmit = async (e) => {
    e.preventDefault();
    const code = $("#login-code").value.trim();
    const btn = codeForm.querySelector("button[type=submit]");
    btn.disabled = true;
    const res = await API.codeCallback(attemptId, code);
    btn.disabled = false;
    if (res.ok) {
      API.setToken(res.data.token);
      toast("Вы вошли!", "ok");
      enterApp();
    } else {
      toast(res.error, "error");
    }
  };
  $("#code-cancel").onclick = () => {
    codeForm.classList.add("hidden");
    loginForm.classList.remove("hidden");
    $("#login-code").value = "";
  };

  // Регистрация
  registerForm.onsubmit = async (e) => {
    e.preventDefault();
    const name = $("#register-name").value.trim();
    const email = $("#register-email").value.trim();
    const password = $("#register-password").value;
    const btn = registerForm.querySelector("button[type=submit]");
    btn.disabled = true;
    const res = await API.register(name, email, password);
    btn.disabled = false;
    if (res.ok) {
      toast("Письмо со ссылкой отправлено на почту. Откройте его, чтобы подтвердить аккаунт.", "ok");
      registerForm.reset();
    } else {
      toast(res.error, "error");
    }
  };
}

/* ============================================================
   Приложение (чат)
   ============================================================ */
const State = {
  user: { id: null, name: null },
  rooms: [],
  filteredRooms: [],
  currentRoom: null,
  messages: [],
  oldestCursor: null,
  hasMore: true,
  ws: null,
  wsReconnectTimer: null,
  searchTimer: null,
  page: 1,
};

async function enterApp() {
  // Получаем пользователя из токена (токен содержит sub = user_id, но имя не знаем).
  // Бэкенд не отдаёт /me, поэтому имя берём из полезной нагрузки токена.
  try {
    const payload = JSON.parse(atob(API.token.split(".")[1]));
    State.user.id = payload.sub;
  } catch {
    State.user.id = "я";
  }
  // Имя пользователя недоступно через API; используем id как заглушку.
  State.user.name = "Вы";

  $("#auth").classList.add("hidden");
  $("#email-callback").classList.add("hidden");
  renderAppShell();
  $("#app").classList.remove("hidden");

  await loadRooms();
}

/* ---------- Каркас приложения ---------- */
function renderAppShell() {
  $("#app").innerHTML = `
    <aside class="sidebar">
      <div class="sidebar-head">
        <span class="brand">EchoMess</span>
        <button class="btn ghost sm" id="create-room-btn" type="button">+ Комната</button>
      </div>
      <div class="sidebar-search">
        <input type="text" id="room-search" placeholder="Поиск комнаты..." autocomplete="off">
      </div>
      <div class="rooms-list" id="rooms-list"></div>
      <div class="sidebar-foot">
        <span class="who" id="who-am-i">${escapeHtml(State.user.name)}</span>
      </div>
    </aside>
    <main class="chat" id="chat-area">
      <div class="chat-empty" id="chat-empty">
        <strong>Выберите комнату</strong>
        <span>Найдите комнату через поиск слева или создайте новую.</span>
      </div>
    </main>
  `;

  $("#create-room-btn").onclick = openCreateRoomModal;

  const searchInput = $("#room-search");
  searchInput.oninput = () => {
    clearTimeout(State.searchTimer);
    State.searchTimer = setTimeout(() => loadRooms(searchInput.value.trim()), 350);
  };
}

/* ---------- Комнаты ---------- */
async function loadRooms(search = "") {
  const res = await API.getRooms(search, 1);
  if (res.ok) {
    State.rooms = res.data || [];
    renderRooms();
  } else {
    if (res.error.includes("401")) {
      showAuth();
    } else {
      toast(res.error, "error");
    }
  }
}

function renderRooms() {
  const list = $("#rooms-list");
  if (!State.rooms.length) {
    list.innerHTML = `<div class="rooms-empty">Комнаты не найдены.<br>Создайте новую!</div>`;
    return;
  }
  list.innerHTML = State.rooms.map((r) => `
    <div class="room-item ${State.currentRoom && State.currentRoom.id === r.id ? "active" : ""}" data-id="${escapeHtml(r.id)}">
      <div style="flex:1;min-width:0">
        <div class="name">${escapeHtml(r.name)}</div>
        <div class="id">${escapeHtml(r.id)}</div>
      </div>
    </div>
  `).join("");
  list.querySelectorAll(".room-item").forEach((el) => {
    el.onclick = () => selectRoom(el.dataset.id);
  });
}

async function selectRoom(roomId) {
  const room = State.rooms.find((r) => r.id === roomId);
  if (!room) return;
  State.currentRoom = room;
  State.messages = [];
  State.oldestCursor = null;
  State.hasMore = true;
  renderRooms();
  renderChatShell();

  await loadInitialMessages();
  connectWebSocket();
}

/* ---------- Окно создания комнаты ---------- */
function openCreateRoomModal() {
  const bg = document.createElement("div");
  bg.className = "modal-bg";
  bg.innerHTML = `
    <div class="modal">
      <h3>Новая комната</h3>
      <form id="new-room-form" class="form">
        <label>
          <span>Название (3–30 символов)</span>
          <input type="text" id="new-room-name" maxlength="30" minlength="3" placeholder="например, Общий чат" required>
        </label>
        <div class="actions">
          <button type="button" class="btn ghost" id="new-room-cancel">Отмена</button>
          <button type="submit" class="btn primary">Создать</button>
        </div>
      </form>
    </div>
  `;
  document.body.appendChild(bg);
  bg.onclick = (e) => { if (e.target === bg) bg.remove(); };
  $("#new-room-cancel").onclick = () => bg.remove();
  $("#new-room-form").onsubmit = async (e) => {
    e.preventDefault();
    const name = $("#new-room-name").value.trim();
    const res = await API.createRoom(name);
    if (res.ok) {
      toast("Комната создана", "ok");
      bg.remove();
      await loadRooms($("#room-search").value.trim());
      selectRoom(res.data);
    } else {
      toast(res.error, "error");
    }
  };
  $("#new-room-name").focus();
}

/* ---------- Чат: отрисовка ---------- */
function renderChatShell() {
  $("#chat-area").innerHTML = `
    <div class="chat-head">
      <div class="title">${escapeHtml(State.currentRoom.name)}</div>
      <span class="status connecting" id="ws-status">подключение...</span>
    </div>
    <div class="messages" id="messages">
      <div class="load-more hidden" id="load-more-wrap">
        <button class="btn ghost sm" id="load-more-btn">Загрузить ещё</button>
      </div>
    </div>
    <form class="composer" id="composer">
      <input type="text" id="message-input" placeholder="Напишите сообщение..." autocomplete="off" maxlength="1000">
      <button type="submit" class="btn primary">Отправить</button>
    </form>
  `;
  $("#composer").onsubmit = (e) => {
    e.preventDefault();
    const input = $("#message-input");
    const text = input.value.trim();
    if (!text || State.ws?.readyState !== WebSocket.OPEN) return;
    State.ws.send(JSON.stringify({ data: text }));
    input.value = "";
  };
  const msgs = $("#messages");
  msgs.onscroll = () => {
    if (msgs.scrollTop < 40 && State.hasMore) loadOlderMessages();
  };
  document.body.classList.add("mobile-chat");
}

/* ---------- Сообщения: загрузка ---------- */
async function loadInitialMessages() {
  const now = new Date().toISOString();
  const res = await API.getMessages(State.currentRoom.id, "before", 50, now);
  if (!res.ok) {
    if (res.error.includes("401")) { showAuth(); return; }
    toast(res.error, "error");
    return;
  }
  const list = res.data || [];
  // API возвращает от новых к старым (desc). Переворачиваем для отображения.
  State.messages = list.slice().reverse();
  if (State.messages.length) {
    State.oldestCursor = State.messages[0].created_at;
  }
  State.hasMore = list.length === 50;
  renderMessages();
}

async function loadOlderMessages() {
  if (!State.hasMore || !State.oldestCursor) return;
  const btn = $("#load-more-btn");
  if (btn) btn.disabled = true;
  const res = await API.getMessages(State.currentRoom.id, "before", 50, State.oldestCursor);
  if (btn) btn.disabled = false;
  if (!res.ok) { toast(res.error, "error"); return; }
  const list = (res.data || []).slice().reverse();
  if (!list.length) { State.hasMore = false; return; }
  const prevScrollHeight = $("#messages").scrollHeight;
  State.messages = list.concat(State.messages);
  State.oldestCursor = State.messages[0].created_at;
  State.hasMore = list.length === 50;
  renderMessages();
  $("#messages").scrollTop = $("#messages").scrollHeight - prevScrollHeight;
}

/* ---------- Сообщения: отрисовка ---------- */
function renderMessages() {
  const container = $("#messages");
  const loadMore = container.querySelector("#load-more-wrap");
  const msgsHtml = State.messages.map((m) => messageHtml(m)).join("");
  container.innerHTML = `
    <div class="load-more ${State.hasMore ? "" : "hidden"}" id="load-more-wrap">
      <button class="btn ghost sm" id="load-more-btn">Загрузить ещё</button>
    </div>
    ${msgsHtml || `<div class="msg sys">Сообщений пока нет. Напишите первым!</div>`}
  `;
  const lmBtn = $("#load-more-btn");
  if (lmBtn) lmBtn.onclick = loadOlderMessages;
  scrollToBottom();
}

function messageHtml(m) {
  const isOwn = m.user_id === State.user.id;
  return `
    <div class="msg ${isOwn ? "own" : ""}">
      ${isOwn ? "" : `<div class="author">${escapeHtml(m.user_name)}</div>`}
      <div>${escapeHtml(m.data)}</div>
      <div class="time">${fmtTime(m.created_at)}</div>
    </div>
  `;
}

function appendMessage(m) {
  State.messages.push(m);
  const container = $("#messages");
  if (!container) return;
  const atBottom = container.scrollHeight - container.scrollTop - container.clientHeight < 60;
  container.insertAdjacentHTML("beforeend", messageHtml(m));
  if (atBottom) scrollToBottom();
}

function scrollToBottom() {
  const c = $("#messages");
  if (c) c.scrollTop = c.scrollHeight;
}

/* ---------- WebSocket ---------- */
function connectWebSocket() {
  if (State.ws) { try { State.ws.close(); } catch {} }
  if (State.wsReconnectTimer) { clearTimeout(State.wsReconnectTimer); State.wsReconnectTimer = null; }

  const proto = location.protocol === "https:" ? "wss" : "ws";
  const url = `${proto}://${location.host}/wc/${State.currentRoom.id}?token=${encodeURIComponent(API.token)}`;
  const ws = new WebSocket(url);
  State.ws = ws;

  const status = $("#ws-status");
  if (status) { status.textContent = "подключение..."; status.className = "status connecting"; }

  ws.onopen = () => {
    if (status) { status.textContent = "на связи"; status.className = "status online"; }
  };
  ws.onmessage = (ev) => {
    try {
      const msg = JSON.parse(ev.data);
      appendMessage(msg);
    } catch {}
  };
  ws.onerror = () => {
    if (status) { status.textContent = "ошибка связи"; status.className = "status"; }
  };
  ws.onclose = () => {
    if (status) { status.textContent = "соединение закрыто"; status.className = "status"; }
    if (State.currentRoom && API.token) {
      State.wsReconnectTimer = setTimeout(() => {
        if (State.currentRoom) connectWebSocket();
      }, 2000);
    }
  };
}
