const API_BASE = "/api";
const TOKEN_KEY = "echomess.accessToken";
const ROOMS_KEY = "echomess.rooms";

const state = {
  mode: "login",
  token: localStorage.getItem(TOKEN_KEY) || "",
  attemptId: "",
  userId: "",
  rooms: loadRooms(),
  activeRoom: null,
  socket: null,
};

const $ = (selector) => document.querySelector(selector);

const els = {
  authGate: $("#authGate"),
  appView: $("#appView"),
  connectionStatus: $("#connectionStatus"),
  refreshSessionBtn: $("#refreshSessionBtn"),
  logoutBtn: $("#logoutBtn"),
  callbackNotice: $("#callbackNotice"),
  loginTab: $("#loginTab"),
  registerTab: $("#registerTab"),
  authTitle: $("#authTitle"),
  authHint: $("#authHint"),
  authUserLabel: $("#authUserLabel"),
  roomTrace: $("#roomTrace"),
  nameField: $("#nameField"),
  authForm: $("#authForm"),
  codeForm: $("#codeForm"),
  nameInput: $("#nameInput"),
  emailInput: $("#emailInput"),
  passwordInput: $("#passwordInput"),
  authSubmitBtn: $("#authSubmitBtn"),
  codeInput: $("#codeInput"),
  createRoomForm: $("#createRoomForm"),
  joinRoomForm: $("#joinRoomForm"),
  clearRoomsBtn: $("#clearRoomsBtn"),
  roomNameInput: $("#roomNameInput"),
  roomIdInput: $("#roomIdInput"),
  roomsList: $("#roomsList"),
  activeRoomTitle: $("#activeRoomTitle"),
  backToRoomsBtn: $("#backToRoomsBtn"),
  loadHistoryBtn: $("#loadHistoryBtn"),
  messages: $("#messages"),
  messageForm: $("#messageForm"),
  messageInput: $("#messageInput"),
  sendMessageBtn: $("#sendMessageBtn"),
  toast: $("#toast"),
};

function loadRooms() {
  try {
    return JSON.parse(localStorage.getItem(ROOMS_KEY) || "[]");
  } catch {
    return [];
  }
}

function saveRooms() {
  localStorage.setItem(ROOMS_KEY, JSON.stringify(state.rooms));
}

function removeRoom(id) {
  state.rooms = state.rooms.filter((item) => item.id !== String(id));
  saveRooms();
  renderRooms();
}

function setActiveView(view) {
  const showRooms = view === "rooms";
  document.body.classList.toggle("view-rooms", showRooms);
  document.body.classList.toggle("view-chat", !showRooms);
}

function setStatus(label, value = "idle") {
  els.connectionStatus.textContent = label;
  els.connectionStatus.dataset.state = value;
}

function setTrace(title, detail = "", value = "ok") {
  els.roomTrace.dataset.state = value;
  els.roomTrace.querySelector("strong").textContent = title;
  els.roomTrace.querySelector("span").textContent = detail;
}

function showToast(message) {
  els.toast.textContent = message;
  els.toast.hidden = false;
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => {
    els.toast.hidden = true;
  }, 3600);
}

function decodeJwtSub(token) {
  try {
    const payload = token.split(".")[1];
    const json = JSON.parse(atob(payload.replace(/-/g, "+").replace(/_/g, "/")));
    return json.sub || "";
  } catch {
    return "";
  }
}

function setToken(token) {
  state.token = token || "";
  state.userId = token ? decodeJwtSub(token) : "";
  if (token) {
    localStorage.setItem(TOKEN_KEY, token);
    setStatus("ready", "online");
    els.authGate.hidden = true;
    els.appView.hidden = false;
    els.authUserLabel.textContent = `Вход выполнен: ${shorten(state.userId)}`;
    setTrace("Авторизация есть", "Теперь можно создавать комнаты и подключаться по ID.", "ok");
  } else {
    localStorage.removeItem(TOKEN_KEY);
    setStatus("offline", "idle");
    els.authGate.hidden = false;
    els.appView.hidden = true;
    els.authUserLabel.textContent = "Вход не выполнен";
    setTrace("Готово", "Войди или зарегистрируйся, потом открывай комнаты.", "warn");
  }
  syncComposer();
}

async function api(path, options = {}, retry = true) {
  const headers = new Headers(options.headers || {});
  if (!(options.body instanceof FormData) && options.body !== undefined) {
    headers.set("Content-Type", "application/json");
  }
  if (state.token) {
    headers.set("Authorization", `Bearer ${state.token}`);
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
    credentials: "include",
  });

  if (response.status === 401 && retry && await refreshSession(false)) {
    return api(path, options, false);
  }

  const text = await response.text();
  let data = null;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }
  }

  if (!response.ok) {
    const detail = data && typeof data === "object" ? data.detail : data;
    const error = new Error(detail || `HTTP ${response.status}`);
    error.status = response.status;
    error.path = path;
    throw error;
  }

  return data;
}

async function refreshSession(notify = true) {
  try {
    const data = await api("/auth/refresh", { method: "GET", headers: {} }, false);
    setToken(data.token);
    if (notify) showToast("Сессия обновлена");
    return true;
  } catch {
    setToken("");
    if (notify) {
      showToast("Сессия не обновилась. Нужно войти заново.");
      setTrace("Сессия истекла", "Backend отклонил refresh. Повтори вход через email и код.", "error");
    }
    return false;
  }
}

function setMode(mode) {
  state.mode = mode;
  const isLogin = mode === "login";
  els.loginTab.classList.toggle("is-active", isLogin);
  els.registerTab.classList.toggle("is-active", !isLogin);
  els.loginTab.setAttribute("aria-selected", String(isLogin));
  els.registerTab.setAttribute("aria-selected", String(!isLogin));
  els.nameField.hidden = isLogin;
  els.nameInput.required = !isLogin;
  els.authSubmitBtn.textContent = isLogin ? "Запросить код" : "Создать аккаунт";
  els.authTitle.textContent = isLogin ? "Войти" : "Регистрация";
  els.authHint.textContent = isLogin
    ? "Введи email и пароль. Затем подтверди одноразовый код из письма."
    : "Создай аккаунт. Backend отправит ссылку подтверждения на email.";
  els.codeForm.hidden = true;
}

function addRoom(room) {
  const normalized = {
    id: String(room.id || room),
    name: room.name || `room:${String(room.id || room).slice(0, 8)}`,
  };
  state.rooms = [normalized, ...state.rooms.filter((item) => item.id !== normalized.id)].slice(0, 16);
  saveRooms();
  renderRooms();
  return normalized;
}

function renderRooms() {
  els.roomsList.innerHTML = "";
  if (!state.rooms.length) {
    const empty = document.createElement("p");
    empty.className = "room-id";
    empty.textContent = "Локальный список пуст.";
    els.roomsList.append(empty);
    return;
  }

  for (const room of state.rooms) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "room-item";
    button.classList.toggle("is-active", state.activeRoom?.id === room.id);
    button.innerHTML = `
      <span class="room-name"></span>
      <span class="room-id"></span>
    `;
    button.querySelector(".room-name").textContent = room.name;
    button.querySelector(".room-id").textContent = room.id;
    button.addEventListener("click", () => selectRoom(room));
    els.roomsList.append(button);
  }
}

function clearMessages() {
  els.messages.innerHTML = "";
}

function ensureMessagesReady() {
  if (els.messages.querySelector(".empty-state")) {
    clearMessages();
  }
}

function renderMessage(message, source = "history") {
  ensureMessagesReady();
  const item = document.createElement("article");
  const mine = message.user_id ? message.user_id === state.userId : source === "local";
  item.className = `message${mine ? " is-mine" : ""}`;

  const body = document.createElement("div");
  body.className = "message-body";
  body.textContent = message.data || "";

  const meta = document.createElement("div");
  meta.className = "message-meta";
  const author = document.createElement("span");
  author.textContent = mine ? "you" : shorten(message.user_id || "live");
  const time = document.createElement("time");
  time.textContent = formatTime(message.created_at || new Date().toISOString());
  meta.append(author, time);

  item.append(body, meta);
  els.messages.append(item);
  els.messages.scrollTop = els.messages.scrollHeight;
}

function formatTime(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "--:--";
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function shorten(value) {
  if (!value) return "";
  return value.length > 10 ? `${value.slice(0, 8)}...` : value;
}

function syncComposer() {
  const ready = Boolean(state.token && state.activeRoom && state.socket?.readyState === WebSocket.OPEN);
  els.messageInput.disabled = !ready;
  els.sendMessageBtn.disabled = !ready;
}

function closeSocket() {
  if (state.socket) {
    state.socket.onclose = null;
    state.socket.close();
    state.socket = null;
  }
  syncComposer();
}

async function selectRoom(room) {
  if (!state.token) {
    setTrace("Нужна авторизация", "Сначала войди, потом открывай комнаты.", "error");
    showToast("Сначала войди");
    setToken("");
    return;
  }
  state.activeRoom = room;
  els.activeRoomTitle.textContent = room.name;
  setTrace("Проверяю комнату", `Загружаю историю и открываю websocket для ${room.id}.`, "warn");
  renderRooms();
  clearMessages();
  setActiveView("chat");
  await loadHistory();
  connectSocket();
}

async function loadHistory() {
  if (!state.activeRoom || !state.token) {
    setTrace("Нужна авторизация", "История сообщений доступна только после входа.", "error");
    showToast("Сначала войди и выбери комнату");
    return;
  }
  try {
    const cursor = encodeURIComponent(new Date().toISOString());
    const data = await api(`/msg/${state.activeRoom.id}?direction=before&limit=60&cursor=${cursor}`);
    clearMessages();
    const messages = Array.isArray(data) ? data.slice().reverse() : [];
    if (!messages.length) {
      els.messages.innerHTML = `
        <div class="empty-state">
          <p class="prompt">quiet room</p>
          <p>История пуста. Первое сообщение задаст тон.</p>
        </div>
      `;
      return;
    }
    messages.forEach((message) => renderMessage(message, "history"));
  } catch (error) {
    if (error.status === 404 && state.activeRoom) {
      dropActiveRoom(`${state.activeRoom.name} не найдена`);
    }
    explainApiError(error, "Не удалось загрузить историю");
  }
}

function dropActiveRoom(reason) {
  if (!state.activeRoom) return;
  removeRoom(state.activeRoom.id);
  state.activeRoom = null;
  els.activeRoomTitle.textContent = "Комната не выбрана";
  closeSocket();
  clearMessages();
  setTrace("Комната удалена", reason, "warn");
  setActiveView("rooms");
}

function connectSocket() {
  closeSocket();
  if (!state.activeRoom || !state.token) {
    setTrace("Нужна авторизация", "WebSocket не открывается без access token.", "error");
    syncComposer();
    return;
  }

  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const token = encodeURIComponent(state.token);
  const url = `${protocol}//${window.location.host}/wc/${state.activeRoom.id}?token=${token}`;
  const socket = new WebSocket(url);
  state.socket = socket;
  setStatus("connecting", "wait");
  syncComposer();

  socket.addEventListener("open", () => {
    setStatus("live", "online");
    setTrace("WebSocket подключен", `Комната ${state.activeRoom.id} готова к сообщениям.`, "ok");
    syncComposer();
  });

  socket.addEventListener("message", (event) => {
    let message;
    try {
      message = JSON.parse(event.data);
    } catch {
      message = { data: event.data, created_at: new Date().toISOString() };
    }

    if (message.type === "err") {
      setTrace("Backend отклонил сообщение", message.data || "Проверь длину и формат сообщения.", "error");
      showToast(message.data || "WebSocket error");
      return;
    }

    if (message.room_id && state.activeRoom?.id !== message.room_id) {
      return;
    }

    renderMessage(message, "live");
  });

  socket.addEventListener("close", (event) => {
    if (state.socket === socket) {
      setStatus(state.token ? "offline" : "signed out", state.token ? "error" : "idle");
      const reason = event.reason || (event.code === 1006 ? "Соединение закрыто без ответа. Часто это 401/403 или несуществующая комната." : `Код закрытия: ${event.code}`);
      if ((event.code === 1006 || event.code === 1008) && state.activeRoom) {
        dropActiveRoom(`Сокет для ${state.activeRoom.name} закрыт: ${reason}`);
        return;
      }
      setTrace("WebSocket закрыт", reason, "error");
      syncComposer();
    }
  });

  socket.addEventListener("error", () => {
    setStatus("socket error", "error");
    setTrace("WebSocket не подключился", "Проверь: ты вошел, token не истек, room id существует.", "error");
    showToast("WebSocket не подключился: нужна авторизация или верный room id");
  });
}

function explainApiError(error, fallback) {
  const status = error.status;
  if (status === 401) {
    setTrace("Нужна авторизация", "Backend вернул 401. Войди заново и повтори действие.", "error");
    setToken("");
  } else if (status === 403) {
    setTrace("Доступ запрещен", "Backend вернул 403. Аккаунт не активен или token не подходит.", "error");
  } else if (status === 400) {
    setTrace(fallback, error.message || "Backend вернул 400. Проверь введенные данные.", "error");
  } else {
    setTrace(fallback, error.message || "Backend не принял запрос.", "error");
  }
  showToast(`${fallback}: ${error.message}`);
}

async function handleCallbackRoute() {
  if (window.location.pathname !== "/auth/url-callback") return;
  const params = new URLSearchParams(window.location.search);
  const token = params.get("token");
  if (!token) return;

  els.callbackNotice.hidden = false;
  try {
    const data = await api(`/auth/url-callback?token=${encodeURIComponent(token)}`, { method: "GET" }, false);
    setToken(data.token);
    window.history.replaceState({}, "", "/");
    els.callbackNotice.hidden = true;
    showToast("Аккаунт подтвержден");
  } catch (error) {
    els.callbackNotice.textContent = error.message;
    showToast(error.message);
  }
}

els.loginTab.addEventListener("click", () => setMode("login"));
els.registerTab.addEventListener("click", () => setMode("register"));

els.authForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const email = els.emailInput.value.trim();
  const password = els.passwordInput.value;

  try {
    if (state.mode === "register") {
      await api("/auth/registry", {
        method: "POST",
        body: JSON.stringify({
          name: els.nameInput.value.trim(),
          email,
          password,
        }),
      }, false);
      showToast("Письмо подтверждения отправлено. Открой ссылку из письма.");
      return;
    }

    const data = await api("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }, false);
    state.attemptId = data.attempt_id;
    els.codeForm.hidden = false;
    els.codeInput.focus();
    showToast("Код отправлен на почту");
  } catch (error) {
    showToast(`Ошибка авторизации: ${error.message}`);
  }
});

els.codeForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!state.attemptId) {
    showToast("Сначала запроси код");
    return;
  }

  try {
    const data = await api("/auth/code-callback", {
      method: "POST",
      body: JSON.stringify({
        attempt_id: state.attemptId,
        code: els.codeInput.value.trim(),
      }),
    }, false);
    setToken(data.token);
    els.codeForm.hidden = true;
    showToast("Вход выполнен");
    if (state.activeRoom) connectSocket();
  } catch (error) {
    showToast(`Код не принят: ${error.message}`);
  }
});

els.createRoomForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!state.token) {
    setTrace("Нужна авторизация", "Создание комнаты требует входа. Сначала авторизуйся.", "error");
    showToast("Сначала войди. Создание комнаты требует авторизацию.");
    setToken("");
    return;
  }
  const name = els.roomNameInput.value.trim();
  if (name.length < 3) {
    showToast("Название от 3 символов");
    return;
  }

  try {
    const id = await api("/room/", {
      method: "POST",
      body: JSON.stringify({ name }),
    }, false);
    const room = addRoom({ id, name });
    els.roomNameInput.value = "";
    await selectRoom(room);
    showToast("Комната создана");
  } catch (error) {
    explainApiError(error, "Комната не создана");
  }
});

els.joinRoomForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!state.token) {
    setTrace("Нужна авторизация", "Подключение к комнате требует входа. Сначала авторизуйся.", "error");
    showToast("Сначала войди. Подключение к комнате требует авторизацию.");
    setToken("");
    return;
  }
  const id = els.roomIdInput.value.trim();
  if (!id) return;

  try {
    const data = await api(`/room/${encodeURIComponent(id)}`, { method: "GET" }, false);
    const room = addRoom({ id: data?.id || id, name: data?.name || `room:${id.slice(0, 8)}` });
    els.roomIdInput.value = "";
    await selectRoom(room);
  } catch (error) {
    if (error.status === 404) removeRoom(id);
    explainApiError(error, "Не удалось подключиться к комнате");
  }
});

els.clearRoomsBtn.addEventListener("click", () => {
  state.rooms = [];
  state.activeRoom = null;
  saveRooms();
  renderRooms();
  closeSocket();
  els.activeRoomTitle.textContent = "Комната не выбрана";
  setTrace("Список очищен", "Локальные ID комнат удалены. Можно создать новую или вставить ID.", "ok");
  setActiveView("rooms");
});

els.backToRoomsBtn.addEventListener("click", () => setActiveView("rooms"));

els.loadHistoryBtn.addEventListener("click", loadHistory);
els.refreshSessionBtn.addEventListener("click", () => refreshSession(true));
els.logoutBtn.addEventListener("click", () => {
  setToken("");
  closeSocket();
  showToast("Локальный токен удален");
});

els.messageForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const text = els.messageInput.value.trim();
  if (!text || !state.socket || state.socket.readyState !== WebSocket.OPEN) return;
  state.socket.send(JSON.stringify({ data: text }));
  els.messageInput.value = "";
  els.messageInput.style.height = "";
});

els.messageInput.addEventListener("input", () => {
  els.messageInput.style.height = "";
  els.messageInput.style.height = `${Math.min(160, els.messageInput.scrollHeight)}px`;
});

els.messageInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    els.messageForm.requestSubmit();
  }
});

setMode("login");
setToken(state.token);
renderRooms();
setActiveView("rooms");
handleCallbackRoute();
if (state.token) refreshSession(false);
