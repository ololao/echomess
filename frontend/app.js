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
  authLoading: false,
};

const $ = (selector) => document.querySelector(selector);

const els = {
  authGate: $("#authGate"),
  landing: $("#landing"),
  enterBtn: $("#enterBtn"),
  landingLoginBtn: $("#landingLoginBtn"),
  landingRegisterBtn: $("#landingRegisterBtn"),
  appView: $("#appView"),
  connectionStatus: $("#connectionStatus"),
  refreshSessionBtn: $("#refreshSessionBtn"),
  logoutBtn: $("#logoutBtn"),
  callbackNotice: $("#callbackNotice"),
  loginTab: $("#loginTab"),
  registerTab: $("#registerTab"),
  authTitle: $("#authTitle"),
  authHint: $("#authHint"),
  authError: $("#authError"),
  authUserLabel: $("#authUserLabel"),
  roomTrace: $("#roomTrace"),
  nameField: $("#nameField"),
  authForm: $("#authForm"),
  codeForm: $("#codeForm"),
  codeResendBtn: $("#codeResendBtn"),
  nameInput: $("#nameInput"),
  emailInput: $("#emailInput"),
  passwordInput: $("#passwordInput"),
  authSubmitBtn: $("#authSubmitBtn"),
  codeInput: $("#codeInput"),
  createRoomForm: $("#createRoomForm"),
  joinRoomForm: $("#joinRoomForm"),
  clearRoomsBtn: $("#clearRoomsBtn"),
  roomNameInput: $("#roomNameInput"),
  roomSearchInput: $("#roomSearchInput"),
  searchResults: $("#searchResults"),
  roomsList: $("#roomsList"),
  activeRoomTitle: $("#activeRoomTitle"),

  backToRoomsBtn: $("#backToRoomsBtn"),
  loadHistoryBtn: $("#loadHistoryBtn"),
  messages: $("#messages"),
  messageForm: $("#messageForm"),
  messageInput: $("#messageInput"),
  sendMessageBtn: $("#sendMessageBtn"),
  composerHint: $("#composerHint"),
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
    setStatus("online", "online");
    els.landing.hidden = true;
    els.authGate.hidden = true;
    els.appView.hidden = false;
    els.authUserLabel.textContent = `${shorten(state.userId)}`;
    setTrace("Авторизация есть", "Создавай комнаты или подключайся по ID.", "ok");
  } else {
    localStorage.removeItem(TOKEN_KEY);
    state.attemptId = "";
    setStatus("offline", "idle");
    els.landing.hidden = false;
    els.authGate.hidden = true;
    els.appView.hidden = true;
    els.authUserLabel.textContent = "Не авторизован";
    setTrace("Нет авторизации", "Войди или зарегистрируйся, потом открывай комнаты.", "warn");
  }
  syncComposer();
}

function showAuthGate(mode = state.mode) {
  els.landing.hidden = true;
  els.authGate.hidden = false;
  els.appView.hidden = true;
  setMode(mode);
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
  state.attemptId = "";
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
    ? "Введи email и пароль — получишь одноразовый код на почту."
    : "Укажи имя, email и пароль. На почту придёт письмо с подтверждением.";
  els.codeForm.hidden = true;
  clearAuthError();
  setAuthLoading(false);
}

function clearAuthError() {
  if (els.authError) {
    els.authError.textContent = "";
    els.authError.hidden = true;
  }
}

function showAuthError(message) {
  if (els.authError) {
    els.authError.textContent = message;
    els.authError.hidden = false;
  } else {
    showToast(message);
  }
}

function setAuthLoading(loading) {
  state.authLoading = loading;
  els.authSubmitBtn.disabled = loading;
  els.authSubmitBtn.dataset.loading = loading ? "true" : "false";
  if (loading) {
    els.authSubmitBtn.dataset.originalText = els.authSubmitBtn.textContent;
    els.authSubmitBtn.textContent = "...";
  } else if (els.authSubmitBtn.dataset.originalText) {
    els.authSubmitBtn.textContent = els.authSubmitBtn.dataset.originalText;
    delete els.authSubmitBtn.dataset.originalText;
  }
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
    empty.className = "rooms-empty";
    empty.textContent = "Список пуст. Создай комнату или подключись по ID.";
    els.roomsList.append(empty);
    return;
  }

  for (const room of state.rooms) {
    const isActive = state.activeRoom?.id === room.id;
    const wrapper = document.createElement("div");
    wrapper.className = `room-item${isActive ? " is-active" : ""}`;

    const selectBtn = document.createElement("button");
    selectBtn.type = "button";
    selectBtn.className = "room-item-main";
    selectBtn.innerHTML = `
      <span class="room-name"></span>
      <span class="room-id"></span>
    `;
    selectBtn.querySelector(".room-name").textContent = room.name;
    selectBtn.querySelector(".room-id").textContent = room.id;
    selectBtn.addEventListener("click", () => selectRoom(room));

    const actions = document.createElement("div");
    actions.className = "room-item-actions";

    const copyBtn = document.createElement("button");
    copyBtn.type = "button";
    copyBtn.className = "room-action-btn";
    copyBtn.title = "Скопировать ID";
    copyBtn.setAttribute("aria-label", "Скопировать ID");
    copyBtn.textContent = "⧉";
    copyBtn.addEventListener("click", (event) => {
      event.stopPropagation();
      copyToClipboard(room.id);
    });

    const removeBtn = document.createElement("button");
    removeBtn.type = "button";
    removeBtn.className = "room-action-btn room-remove-btn";
    removeBtn.title = "Убрать из списка";
    removeBtn.setAttribute("aria-label", "Убрать комнату из списка");
    removeBtn.textContent = "×";
    removeBtn.addEventListener("click", (event) => {
      event.stopPropagation();
      if (state.activeRoom?.id === room.id) {
        closeSocket();
        state.activeRoom = null;
        setActiveView("rooms");
      }
      removeRoom(room.id);
    });

    actions.append(copyBtn, removeBtn);
    wrapper.append(selectBtn, actions);
    els.roomsList.append(wrapper);
  }
}

async function copyToClipboard(value) {
  try {
    await navigator.clipboard.writeText(value);
    showToast("ID скопирован");
  } catch {
    const textarea = document.createElement("textarea");
    textarea.value = value;
    textarea.style.position = "fixed";
    textarea.style.opacity = "0";
    document.body.append(textarea);
    textarea.select();
    try {
      document.execCommand("copy");
      showToast("ID скопирован");
    } catch {
      showToast("Не удалось скопировать");
    }
    textarea.remove();
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
  const hasToken = Boolean(state.token);
  const hasRoom = Boolean(state.activeRoom);
  const isOpen = state.socket?.readyState === WebSocket.OPEN;
  const ready = hasToken && hasRoom && isOpen;

  els.messageInput.disabled = !ready;
  els.sendMessageBtn.disabled = !ready;

  if (els.composerHint) {
    if (!hasToken) {
      els.composerHint.textContent = "Войдите в аккаунт, чтобы писать сообщения";
      els.composerHint.hidden = false;
    } else if (!hasRoom) {
      els.composerHint.textContent = "Выберите или создайте комнату";
      els.composerHint.hidden = false;
    } else if (!isOpen) {
      els.composerHint.textContent = "Подключение...";
      els.composerHint.hidden = false;
    } else {
      els.composerHint.hidden = true;
    }
  }

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
  els.messages.innerHTML = `<div class="empty-state"><p class="rooms-empty">Загрузка...</p></div>`;
  try {
    const cursor = encodeURIComponent(new Date().toISOString());
    const data = await api(`/msg/${state.activeRoom.id}?direction=before&limit=60&cursor=${cursor}`);
    clearMessages();
    const messages = Array.isArray(data) ? data.slice().reverse() : [];
    if (!messages.length) {
      els.messages.innerHTML = `
        <div class="empty-state">
          <p class="prompt">тишина</p>
          <p>Здесь пока нет сообщений. Напиши первым!</p>
        </div>
      `;
      return;
    }
    messages.forEach((message) => renderMessage(message, "history"));
  } catch (error) {
    if (error.status === 404 && state.activeRoom) {
      dropActiveRoom(`Комната «${state.activeRoom.name}» не найдена на сервере`);
      return;
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
  setStatus("подключение", "wait");
  syncComposer();

  socket.addEventListener("open", () => {
    setStatus("онлайн", "online");
    setTrace("Подключено", `Комната «${state.activeRoom?.name}» готова. Пиши сообщения!`, "ok");
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
      setTrace("Сообщение не отправлено", message.data || "Проверь длину и формат сообщения.", "error");
      showToast(message.data || "Ошибка отправки");
      return;
    }

    if (message.room_id && state.activeRoom?.id !== message.room_id) {
      return;
    }

    renderMessage(message, "live");
  });

  socket.addEventListener("close", (event) => {
    if (state.socket === socket) {
      const isAuth = Boolean(state.token);
      setStatus(isAuth ? "офлайн" : "не авторизован", isAuth ? "error" : "idle");
      const reason = event.reason
        || (event.code === 1006 ? "Соединение прервано. Возможно, комната не существует или истёк токен." : `Код: ${event.code}`);
      if ((event.code === 1006 || event.code === 1008) && state.activeRoom) {
        dropActiveRoom(`Соединение с «${state.activeRoom.name}» прервано: ${reason}`);
        return;
      }
      setTrace("Соединение закрыто", reason, "error");
      syncComposer();
    }
  });

  socket.addEventListener("error", () => {
    setStatus("ошибка", "error");
    setTrace("Нет соединения", "Проверь: ты авторизован, токен актуален, комната существует.", "error");
    showToast("WebSocket не подключился");
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

els.enterBtn.addEventListener("click", () => showAuthGate("login"));
els.landingLoginBtn.addEventListener("click", () => showAuthGate("login"));
els.landingRegisterBtn.addEventListener("click", () => showAuthGate("register"));

els.authForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearAuthError();
  const email = els.emailInput.value.trim();
  const password = els.passwordInput.value;

  setAuthLoading(true);
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
      setAuthLoading(false);
      showToast("Письмо подтверждения отправлено — открой ссылку из письма");
      els.authHint.textContent = `Письмо отправлено на ${email}. Перейди по ссылке из письма для активации аккаунта.`;
      return;
    }

    const data = await api("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }, false);
    state.attemptId = data.attempt_id;
    els.codeForm.hidden = false;
    els.codeInput.value = "";
    els.codeInput.focus();
    showToast("Код отправлен на почту");
  } catch (error) {
    showAuthError(error.message || "Ошибка авторизации");
  } finally {
    setAuthLoading(false);
  }
});

els.codeForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!state.attemptId) {
    showAuthError("Сначала запроси код через форму выше");
    return;
  }

  const codeSubmitBtn = els.codeForm.querySelector("button[type=submit]");
  const originalText = codeSubmitBtn.textContent;
  codeSubmitBtn.disabled = true;
  codeSubmitBtn.textContent = "...";

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
    showToast("Вход выполнен!");
    if (state.activeRoom) connectSocket();
  } catch (error) {
    showAuthError(error.message || "Код не принят");
    els.codeInput.select();
  } finally {
    codeSubmitBtn.disabled = false;
    codeSubmitBtn.textContent = originalText;
  }
});

if (els.codeResendBtn) {
  els.codeResendBtn.addEventListener("click", async () => {
    if (!els.emailInput.value || !els.passwordInput.value) {
      showAuthError("Заполни email и пароль выше");
      return;
    }
    els.codeResendBtn.disabled = true;
    try {
      const data = await api("/auth/login", {
        method: "POST",
        body: JSON.stringify({
          email: els.emailInput.value.trim(),
          password: els.passwordInput.value,
        }),
      }, false);
      state.attemptId = data.attempt_id;
      els.codeInput.value = "";
      els.codeInput.focus();
      showToast("Новый код отправлен");
    } catch (error) {
      showAuthError(error.message || "Не удалось выслать код");
    } finally {
      els.codeResendBtn.disabled = false;
    }
  });
}

els.createRoomForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!state.token) {
    setTrace("Нужна авторизация", "Создание комнаты требует входа.", "error");
    showToast("Войди в аккаунт, чтобы создавать комнаты");
    return;
  }
  const name = els.roomNameInput.value.trim();
  if (name.length < 3) {
    showToast("Название от 3 символов");
    return;
  }

  const createBtn = els.createRoomForm.querySelector("button[type=submit]");
  createBtn.disabled = true;
  const origText = createBtn.textContent;
  createBtn.textContent = "...";

  try {
    const id = await api("/room/", {
      method: "POST",
      body: JSON.stringify({ name }),
    }, false);
    const room = addRoom({ id, name });
    els.roomNameInput.value = "";
    await selectRoom(room);
    showToast(`Комната «${name}» создана`);
  } catch (error) {
    explainApiError(error, "Комната не создана");
  } finally {
    createBtn.disabled = false;
    createBtn.textContent = origText;
  }
});

function renderSearchResults(rooms) {
  const container = els.searchResults;
  container.innerHTML = "";
  if (!rooms.length) {
    container.hidden = false;
    const empty = document.createElement("p");
    empty.className = "rooms-empty";
    empty.textContent = "Ничего не найдено";
    container.append(empty);
    return;
  }
  container.hidden = false;
  for (const room of rooms) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "search-result-item";
    btn.innerHTML = `<span class="room-name"></span><span class="room-id"></span>`;
    btn.querySelector(".room-name").textContent = room.name;
    btn.querySelector(".room-id").textContent = room.id;
    btn.addEventListener("click", async () => {
      container.hidden = true;
      els.roomSearchInput.value = "";
      const r = addRoom({ id: room.id, name: room.name });
      await selectRoom(r);
    });
    container.append(btn);
  }
}

els.joinRoomForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!state.token) {
    setTrace("Нужна авторизация", "Подключение к комнате требует входа.", "error");
    showToast("Войди в аккаунт, чтобы подключаться к комнатам");
    return;
  }
  const query = els.roomSearchInput.value.trim();
  if (!query) return;

  const joinBtn = els.joinRoomForm.querySelector("button[type=submit]");
  joinBtn.disabled = true;
  const origJoinText = joinBtn.textContent;
  joinBtn.textContent = "...";

  try {
    const results = await api(
      `/room/?search=${encodeURIComponent(query)}&page_number=1&page_limit=10`,
      { method: "GET" },
    );
    renderSearchResults(Array.isArray(results) ? results : []);
  } catch (error) {
    explainApiError(error, "Поиск не удался");
  } finally {
    joinBtn.disabled = false;
    joinBtn.textContent = origJoinText;
  }
});

els.roomSearchInput.addEventListener("input", () => {
  if (!els.roomSearchInput.value.trim()) {
    els.searchResults.hidden = true;
    els.searchResults.innerHTML = "";
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
