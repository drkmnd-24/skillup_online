/**
 * SkillUp Frontend Auth helper (vanilla JS)
 * - Logs in via SimpleJWT: POST /api/token/
 * - Stores access/refresh in sessionStorage (or localStorage if 'remember me')
 * - Provides authFetch() that auto-attaches Authorization and refreshes on 401
 * - Exposes window.Auth for use across pages
 */

(function () {
    const CONFIG = {
        API_BASE: window.APP_API_BASE || "/api",
        TOKEN_ENDPOINT: "/token/",
        REFRESH_ENDPOINT: "/token/refresh/",
        STORAGE_KEY: "skillup_jwt",
        REDIRECT_AFTER_LOGIN: "/", // fallback if login form doesn't set data-redirect
    };

    // ---- storage helpers ----
    function getStorage(persist) {
        return persist ? window.localStorage : window.sessionStorage;
    }

    function clearBoth() {
        try {
            window.localStorage.removeItem(CONFIG.STORAGE_KEY);
        } catch (e) {
        }
        try {
            window.sessionStorage.removeItem(CONFIG.STORAGE_KEY);
        } catch (e) {
        }
    }

    function readTokens() {
        const raw = window.sessionStorage.getItem(CONFIG.STORAGE_KEY)
            || window.localStorage.getItem(CONFIG.STORAGE_KEY);
        if (!raw) return null;
        try {
            return JSON.parse(raw);
        } catch (e) {
            return null;
        }
    }

    function saveTokens(tokens, persist) {
        clearBoth();
        const storage = getStorage(persist);
        storage.setItem(CONFIG.STORAGE_KEY, JSON.stringify({
            ...tokens,
            persist: !!persist,
            saved_at: Date.now()
        }));
    }

    function getAccessToken() {
        const stored = readTokens();
        return stored && stored.access ? stored.access : null;
    }

    function isLoggedIn() {
        return !!getAccessToken();
    }

    function logout() {
        clearBoth();
    }

    // ---- network: login & refresh ----
    async function login(username, password, remember = false) {
        const url = CONFIG.API_BASE + CONFIG.TOKEN_ENDPOINT;
        const res = await fetch(url, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({username, password}),
            credentials: "same-origin",
        });

        const data = await res.json().catch(() => ({}));
        if (!res.ok) {
            const msg = (data && (data.detail || data.non_field_errors)) || "Invalid credentials";
            throw new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
        }
        if (!data.access || !data.refresh) {
            throw new Error("Invalid token response");
        }

        saveTokens({access: data.access, refresh: data.refresh}, remember);
        return data;
    }

    async function refreshTokens() {
        const stored = readTokens();
        if (!stored || !stored.refresh) throw new Error("No refresh token available");

        const url = CONFIG.API_BASE + CONFIG.REFRESH_ENDPOINT;
        const res = await fetch(url, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({refresh: stored.refresh}),
            credentials: "same-origin",
        });

        const data = await res.json().catch(() => ({}));
        if (!res.ok || !data.access) {
            logout();
            throw new Error("Refresh token expired");
        }
        saveTokens({access: data.access, refresh: stored.refresh}, !!stored.persist);
        return data;
    }

    // ---- fetch wrapper with auto attach + retry-once ----
    async function authFetch(input, init = {}) {
        const tokens = readTokens();
        const headers = new Headers(init && init.headers || {});
        if (tokens && tokens.access && !headers.has("Authorization")) {
            headers.set("Authorization", "Bearer " + tokens.access);
        }
        let res = await fetch(new Request(input, {...init, headers}));

        if (res.status !== 401) return res;

        // Try one refresh, then retry original request
        try {
            await refreshTokens();
            const refreshed = readTokens();
            const headers2 = new Headers(init && init.headers || {});
            headers2.set("Authorization", "Bearer " + refreshed.access);
            res = await fetch(new Request(input, {...init, headers: headers2}));
            return res;
        } catch (e) {
            return res; // still 401; caller can handle
        }
    }

    // ---- form wiring (supports old & new IDs) ----
    function q(id) {
        return document.getElementById(id);
    }

    function wireLoginForm() {
        const form = q("loginForm") || q("login-form");
        if (!form) return;

        const userEl = q("usernameInput") || q("user_login");
        const passEl = q("passwordInput") || q("user_pass");
        const rememberEl = q("rememberCheck") || q("keepLogged");
        const btn = q("loginBtn") || form.querySelector('button[type="submit"]');
        const errorBox = q("loginError");

        form.addEventListener("submit", async function (e) {
            e.preventDefault();
            if (btn) {
                btn.disabled = true;
                btn.classList.add("disabled");
            }

            const username = (userEl && userEl.value || "").trim();
            const password = (passEl && passEl.value || "");
            const remember = !!(rememberEl && rememberEl.checked);

            if (errorBox) {
                errorBox.classList.add("d-none");
                errorBox.innerText = "";
            }

            try {
                await login(username, password, remember);
                const redirectTo = form.dataset.redirect || CONFIG.REDIRECT_AFTER_LOGIN;
                window.location.assign(redirectTo);
            } catch (err) {
                const msg = (err && err.message) ? err.message : "Login failed";
                if (errorBox) {
                    errorBox.innerText = msg;
                    errorBox.classList.remove("d-none");
                } else {
                    alert(msg);
                }
            } finally {
                if (btn) {
                    btn.disabled = false;
                    btn.classList.remove("disabled");
                }
            }
        });
    }

    // ---- expose API ----
    window.Auth = {
        login, logout, isLoggedIn, getAccessToken, refreshTokens, authFetch, readTokens
    };

    document.addEventListener("DOMContentLoaded", wireLoginForm);
})();
