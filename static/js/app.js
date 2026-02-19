/* Nova Poshta Tracking v1.1 — app.js */

function syncAPI(apiKeyId) {
    const btn = document.getElementById(`sync-btn-${apiKeyId}`);
    if (!btn) return;
    const orig = btn.innerHTML;
    const txt  = window.translations?.syncing || 'Syncing...';

    btn.disabled = true;
    btn.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span>${txt}`;

    fetch(`/sync/${apiKeyId}`, { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                showToast('success', data.message || window.translations?.syncSuccess || 'Done!');
                setTimeout(() => location.reload(), 1500);
            } else {
                showToast('danger', (window.translations?.syncError || 'Error: ') + (data.error || ''));
                btn.disabled = false;
                btn.innerHTML = orig;
            }
        })
        .catch(e => {
            showToast('danger', e.message);
            btn.disabled = false;
            btn.innerHTML = orig;
        });
}

function syncAll() {
    const btn = document.getElementById('sync-all-btn');
    if (!btn) return;
    const orig = btn.innerHTML;
    const txt  = window.translations?.syncing || 'Syncing...';
    
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span>${txt}`;
    
    fetch('/sync/all', { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                showToast('success', data.message, 8000);
                setTimeout(() => location.reload(), 2000);
            } else {
                showToast('danger', data.error || 'Sync failed');
                btn.disabled = false;
                btn.innerHTML = orig;
            }
        })
        .catch(e => {
            showToast('danger', e.message);
            btn.disabled = false;
            btn.innerHTML = orig;
        });
}

function showToast(type, message, duration = 6000) {
    const wrap = document.querySelector('.container-fluid') || document.body;
    const div = document.createElement('div');
    div.className = `alert alert-${type} alert-dismissible fade show`;
    div.style.position = 'relative';
    div.style.zIndex = '9999';
    div.innerHTML = `${message}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
    wrap.prepend(div);
    setTimeout(() => { 
        div.classList.remove('show'); 
        setTimeout(() => div.remove(), 300); 
    }, duration);
}

// Auto-dismiss flash messages
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.alert:not(.alert-permanent)').forEach(a => {
        setTimeout(() => { 
            a.classList.remove('show'); 
            setTimeout(() => a.remove(), 300); 
        }, 6000);
    });
    
    // Tooltips
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(el => new bootstrap.Tooltip(el));
});

window.syncAPI   = syncAPI;
window.syncAll   = syncAll;
window.showToast = showToast;
