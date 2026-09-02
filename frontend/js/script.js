/**
 * script.js — Login page logic for MH Digital ID System
 */

const API = 'http://127.0.0.1:8000/api';

// ─── Password Show / Hide ─────────────────────────────────────────

const togglePassword = document.getElementById('togglePassword');
const passwordInput  = document.getElementById('password');
const eyeIcon        = document.getElementById('eyeIcon');

if (togglePassword) {
    togglePassword.addEventListener('click', function () {
        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
            eyeIcon.classList.replace('bi-eye', 'bi-eye-slash');
        } else {
            passwordInput.type = 'password';
            eyeIcon.classList.replace('bi-eye-slash', 'bi-eye');
        }
    });
}

// ─── Auto-redirect if already logged in ──────────────────────────

(async function checkAlreadyLoggedIn() {
    try {
        const res = await fetch(`${API}/auth/me/`, { credentials: 'include' });
        if (res.ok) {
            const d = await res.json();
            if (d.success) {
                window.location.href = 'dashboard.html';
            }
        }
    } catch {}
})();

// ─── Login Form ───────────────────────────────────────────────────

const loginForm = document.getElementById('loginForm');

if (loginForm) {
    loginForm.addEventListener('submit', async function (e) {
        e.preventDefault();

        const button      = document.getElementById('loginButton');
        const buttonText  = document.getElementById('buttonText');
        const loader      = document.getElementById('buttonLoader');
        const loginMsg    = document.getElementById('loginMessage');

        const email    = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;

        // Client-side validation
        if (!email || !email.includes('@')) {
            loginMsg.innerHTML = `<div class="alert alert-danger">Please enter a valid email address.</div>`;
            return;
        }
        if (!password) {
            loginMsg.innerHTML = `<div class="alert alert-danger">Please enter your password.</div>`;
            return;
        }

        // Show loading state
        button.disabled      = true;
        buttonText.textContent = 'Signing in...';
        loader.classList.remove('d-none');
        loginMsg.innerHTML   = '';

        try {
            const response = await fetch(`${API}/auth/login/`, {
                method:      'POST',
                credentials: 'include',
                headers:     { 'Content-Type': 'application/json' },
                body:        JSON.stringify({ email, password }),
            });

            const data = await response.json();

            if (response.ok && data.success) {
                loginMsg.innerHTML = `<div class="alert alert-success">
                    <i class="bi bi-check-circle me-2"></i>${data.message}
                </div>`;
                // Redirect after short delay
                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 600);
            } else {
                loginMsg.innerHTML = `<div class="alert alert-danger">
                    <i class="bi bi-exclamation-circle me-2"></i>${data.message || 'Login failed. Please try again.'}
                </div>`;
                // Shake the card
                const card = document.querySelector('.login-card');
                if (card) {
                    card.style.animation = 'none';
                    card.offsetHeight; // reflow
                    card.style.animation = 'shake 0.4s ease';
                }
            }

        } catch (error) {
            loginMsg.innerHTML = `<div class="alert alert-danger">
                <i class="bi bi-wifi-off me-2"></i>Unable to connect to server. Please try again.
            </div>`;
        }

        // Reset button
        button.disabled       = false;
        buttonText.textContent = 'Sign In';
        loader.classList.add('d-none');
    });
}

// Add shake animation style
const shakeStyle = document.createElement('style');
shakeStyle.textContent = `
    @keyframes shake {
        0%,100%{transform:translateX(0)}
        20%{transform:translateX(-8px)}
        40%{transform:translateX(8px)}
        60%{transform:translateX(-6px)}
        80%{transform:translateX(6px)}
    }
`;
document.head.appendChild(shakeStyle);
