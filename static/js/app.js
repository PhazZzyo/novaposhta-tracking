/* Nova Poshta Tracking — app.js */

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
                setTimeout(() => location.reload(), 1200);
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

function showToast(type, message) {
    const wrap = document.querySelector('.container-fluid');
    if (!wrap) return;
    const div = document.createElement('div');
    div.className = `alert alert-${type} alert-dismissible fade show`;
    div.innerHTML = `${message}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
    wrap.prepend(div);
    setTimeout(() => { div.classList.remove('show'); setTimeout(() => div.remove(), 300); }, 5000);
}

// Auto-dismiss flash messages
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.alert:not(.alert-permanent)').forEach(a => {
        setTimeout(() => { a.classList.remove('show'); setTimeout(() => a.remove(), 300); }, 6000);
    });
    // Tooltips
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => new bootstrap.Tooltip(el));
});

window.syncAPI   = syncAPI;
window.showToast = showToast;
