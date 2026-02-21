/**
 * auth.js – lightweight client-side auth with login / logout support.
 *
 * Session data is stored in sessionStorage so it is automatically cleared
 * when the browser tab is closed, which is the expected behaviour for a
 * session token that is not explicitly persisted.
 */

const SESSION_KEY = 'auth_session';

// --- Demo credential store -------------------------------------------------
// In a real application credentials are validated server-side.
const DEMO_USERS = {
  admin: 'password',
  user:  'letmein',
};

// --- Session helpers -------------------------------------------------------

/**
 * Create a session token and persist it to sessionStorage.
 * @param {string} username
 */
function createSession(username) {
  const token = btoa(`${username}:${Date.now()}:${Math.random()}`);
  const session = { username, token, loginAt: new Date().toISOString() };
  sessionStorage.setItem(SESSION_KEY, JSON.stringify(session));
  return session;
}

/**
 * Return the current session object, or null if not logged in.
 * @returns {{ username: string, token: string, loginAt: string } | null}
 */
function getSession() {
  try {
    const raw = sessionStorage.getItem(SESSION_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

/**
 * Destroy the current session.
 *
 * Steps performed:
 *  1. Remove the session record from sessionStorage.
 *  2. (Hook point) In a real app you would also call a server endpoint
 *     (e.g. POST /api/logout) so the server-side token is invalidated.
 *  3. Redirect to the login view.
 */
function logout() {
  sessionStorage.removeItem(SESSION_KEY);
  // Optionally: document.cookie = 'session=; Max-Age=0; path=/'; (server cookies)
  showLogin();
}

// --- UI helpers ------------------------------------------------------------

function showLogin(errorMsg) {
  document.getElementById('dashboard').style.display = 'none';
  document.getElementById('loginForm').style.display  = 'block';
  document.getElementById('username').value  = '';
  document.getElementById('password').value  = '';
  document.getElementById('error').textContent = errorMsg || '';
}

function showDashboard(session) {
  document.getElementById('loginForm').style.display  = 'none';
  document.getElementById('dashboard').style.display  = 'block';
  document.getElementById('welcomeMsg').textContent =
    `Logged in as ${session.username} (since ${new Date(session.loginAt).toLocaleTimeString()})`;
}

// --- Login handler ---------------------------------------------------------

function handleLogin() {
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value;

  if (!username || !password) {
    document.getElementById('error').textContent = 'Please enter username and password.';
    return;
  }

  if (DEMO_USERS[username] !== password) {
    document.getElementById('error').textContent = 'Invalid username or password.';
    return;
  }

  const session = createSession(username);
  showDashboard(session);
}

// --- Bootstrap -------------------------------------------------------------

document.addEventListener('DOMContentLoaded', () => {
  // Wire up buttons
  document.getElementById('loginBtn').addEventListener('click', handleLogin);
  document.getElementById('logoutBtn').addEventListener('click', logout);

  // Allow Enter key to submit the login form
  document.getElementById('password').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') handleLogin();
  });

  // Restore existing session on page load
  const session = getSession();
  if (session) {
    showDashboard(session);
  } else {
    showLogin();
  }
});
