/**
 * app.js — Shared utilities for MH Digital ID System
 */

const API_BASE = 'http://127.0.0.1:8000/api';

// ─── Auth helpers ─────────────────────────────────────────────────

async function checkAuth() {
    try {
        const res = await fetch(`${API_BASE}/auth/me/`, { credentials: 'include' });
        if (!res.ok) return null;
        const d = await res.json();
        return d.success ? d.user : null;
    } catch {
        return null;
    }
}

async function doLogout() {
    try {
        await fetch(`${API_BASE}/auth/logout/`, { method: 'POST', credentials: 'include' });
    } catch {}
    window.location.href = 'index.html';
}

// ─── Date formatting ──────────────────────────────────────────────

function formatDate(s) {
    if (!s) return '—';
    const d = new Date(s);
    return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
}

function formatDateTime(s) {
    if (!s) return '—';
    const d = new Date(s);
    return d.toLocaleString('en-IN', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function timeAgo(iso) {
    const diff = (Date.now() - new Date(iso).getTime()) / 1000;
    if (diff < 60)    return `${Math.floor(diff)}s ago`;
    if (diff < 3600)  return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
}

// ─── Role label ───────────────────────────────────────────────────

function roleLabel(role) {
    const map = { superadmin: 'Super Admin', admin: 'HR / Admin', employee: 'Employee' };
    return map[role] || role;
}

// ─── Toast notification ───────────────────────────────────────────

function showToast(message, type = 'success') {
    const existing = document.getElementById('_toast');
    if (existing) existing.remove();

    const colors = { success: '#16a34a', error: '#ef4444', warning: '#f59e0b', info: '#0d6efd' };
    const icons  = { success: 'bi-check-circle-fill', error: 'bi-x-circle-fill', warning: 'bi-exclamation-triangle-fill', info: 'bi-info-circle-fill' };

    const toast = document.createElement('div');
    toast.id = '_toast';
    toast.style.cssText = `
        position:fixed; bottom:28px; right:28px; z-index:9999;
        background:#fff; border-radius:14px; padding:14px 20px;
        box-shadow:0 8px 32px rgba(0,0,0,0.14);
        display:flex; align-items:center; gap:12px;
        font-size:14px; font-weight:600; color:#1f2937;
        animation:slideUp 0.3s ease forwards; min-width:280px;
        border-left:4px solid ${colors[type] || colors.info};
    `;
    toast.innerHTML = `
        <i class="bi ${icons[type] || icons.info}" style="color:${colors[type]};font-size:18px;"></i>
        <span>${message}</span>
        <button onclick="this.parentElement.remove()" style="margin-left:auto;border:none;background:transparent;color:#9ca3af;cursor:pointer;font-size:16px;">×</button>
    `;

    // Add animation keyframes if not present
    if (!document.getElementById('_toastStyle')) {
        const style = document.createElement('style');
        style.id = '_toastStyle';
        style.textContent = '@keyframes slideUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}';
        document.head.appendChild(style);
    }

    document.body.appendChild(toast);
    setTimeout(() => { if (toast.parentElement) toast.remove(); }, 4000);
}
