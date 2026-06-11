/**
 * MosaVerse Admin API — Authentication & CRUD helpers
 */

const AdminAPI = {
    // ─── Auth ──────────────────────────────────────────

    isAuthenticated() {
        const user = this.getUser();
        return user && user.is_staff;
    },

    getUser() {
        return JSON.parse(localStorage.getItem('mosaverse_user') || 'null');
    },

    requireAuth() {
        if (!this.isAuthenticated()) {
            window.location.href = 'admin-login.html';
        }
    },

    async login(username, password) {
        const data = await API.post('/login/', { username, password });
        if (data.user) {
            localStorage.setItem('mosaverse_user', JSON.stringify(data.user));
        }
        return data;
    },

    async logout() {
        try { await API.post('/logout/'); } catch (_) { /* ignore */ }
        localStorage.removeItem('mosaverse_user');
        window.location.href = 'index.html';
    },

    // ─── Dashboard ─────────────────────────────────────

    getStats() {
        return API.get('/dashboard/stats/');
    },

    // ─── Design CRUD ───────────────────────────────────

    createDesign(formData) {
        return API.upload('/designs/create/', formData);
    },

    updateDesign(id, formData) {
        return API.uploadPut(`/designs/${id}/update/`, formData);
    },

    deleteDesign(id) {
        return API.delete(`/designs/${id}/delete/`);
    },

    togglePublish(id) {
        return API.post(`/designs/${id}/toggle-publish/`);
    },

    // ─── AI ────────────────────────────────────────────

    generateDescription(title, category, designId) {
        return API.post('/ai/generate-description/', { title, category, design_id: designId });
    },

    generateCategory(title, description, designId) {
        return API.post('/ai/generate-category/', { title, description, design_id: designId });
    },

    // ─── Category CRUD ─────────────────────────────────

    getCategories() {
        return API.get('/categories/');
    },

    createCategory(name, description = '') {
        return API.post('/categories/', { name, description });
    },

    updateCategory(id, data) {
        return API.put(`/categories/${id}/`, data);
    },

    deleteCategory(id) {
        return API.delete(`/categories/${id}/`);
    },
};

// ─── Toast Notification ────────────────────────────────

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    if (!toast) return;

    toast.textContent = message;
    toast.className = 'fixed bottom-6 right-6 z-[110] px-5 py-3 rounded-xl text-sm font-semibold shadow-lg';

    const colorMap = {
        success: ['bg-green-600', 'text-white'],
        error: ['bg-red-600', 'text-white'],
        warning: ['bg-yellow-500', 'text-white'],
    };
    const colors = colorMap[type] || ['bg-gray-900', 'text-white'];
    toast.classList.add(...colors);
    toast.classList.remove('hidden');

    setTimeout(() => toast.classList.add('hidden'), 3000);
}

// ─── Logout Setup ──────────────────────────────────────

function setupLogout() {
    const btn = document.getElementById('logoutBtn');
    if (btn) btn.addEventListener('click', () => AdminAPI.logout());
}
