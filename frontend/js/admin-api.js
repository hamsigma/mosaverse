/**
 * MosaVerse Admin API — Authentication & CRUD helpers
 */

const AdminAPI = {
    /**
     * Check if user is authenticated
     */
    isAuthenticated() {
        const user = JSON.parse(localStorage.getItem('mosaverse_user') || 'null');
        return user && user.is_staff;
    },

    /**
     * Get current user from localStorage
     */
    getUser() {
        return JSON.parse(localStorage.getItem('mosaverse_user') || 'null');
    },

    /**
     * Require authentication — redirect to login if not authenticated
     */
    requireAuth() {
        if (!this.isAuthenticated()) {
            window.location.href = 'admin-login.html';
        }
    },

    /**
     * Login
     */
    async login(username, password) {
        const data = await API.post('/login/', { username, password });
        if (data.user) {
            localStorage.setItem('mosaverse_user', JSON.stringify(data.user));
        }
        return data;
    },

    /**
     * Logout
     */
    async logout() {
        try {
            await API.post('/logout/');
        } catch (e) {
            // Ignore errors
        }
        localStorage.removeItem('mosaverse_user');
        window.location.href = 'admin-login.html';
    },

    /**
     * Get dashboard stats
     */
    async getStats() {
        return API.get('/dashboard/stats/');
    },

    /**
     * Create design (multipart/form-data for image upload)
     */
    async createDesign(formData) {
        const csrfToken = getCookie('csrftoken');
        const headers = {};
        if (csrfToken) headers['X-CSRFToken'] = csrfToken;

        const response = await fetch(`${API_BASE}/designs/create/`, {
            method: 'POST',
            headers,
            credentials: 'include',
            body: formData,
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(JSON.stringify(errData));
        }

        return response.json();
    },

    /**
     * Update design
     */
    async updateDesign(id, formData) {
        const csrfToken = getCookie('csrftoken');
        const headers = {};
        if (csrfToken) headers['X-CSRFToken'] = csrfToken;

        const response = await fetch(`${API_BASE}/designs/${id}/update/`, {
            method: 'PUT',
            headers,
            credentials: 'include',
            body: formData,
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(JSON.stringify(errData));
        }

        return response.json();
    },

    /**
     * Delete design
     */
    async deleteDesign(id) {
        const csrfToken = getCookie('csrftoken');
        const headers = { 'Content-Type': 'application/json' };
        if (csrfToken) headers['X-CSRFToken'] = csrfToken;

        const response = await fetch(`${API_BASE}/designs/${id}/delete/`, {
            method: 'DELETE',
            headers,
            credentials: 'include',
        });

        if (!response.ok && response.status !== 204) {
            throw new Error(`Delete failed: ${response.status}`);
        }

        return true;
    },

    /**
     * Generate description with AI
     */
    async generateDescription(title, category, designId) {
        return API.post('/ai/generate-description/', { title, category, design_id: designId });
    },

    /**
     * Generate category with AI
     */
    async generateCategory(title, description, designId) {
        return API.post('/ai/generate-category/', { title, description, design_id: designId });
    },
};

/**
 * Show toast notification
 */
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    if (!toast) return;

    toast.textContent = message;
    toast.className = 'fixed bottom-6 right-6 z-[110] px-5 py-3 rounded-btn text-sm font-semibold shadow-lg';

    if (type === 'success') {
        toast.classList.add('bg-green-600', 'text-white');
    } else if (type === 'error') {
        toast.classList.add('bg-red-600', 'text-white');
    } else {
        toast.classList.add('bg-primary', 'text-accent');
    }

    toast.classList.remove('hidden');

    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}

/**
 * Setup logout button on all admin pages
 */
function setupLogout() {
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => AdminAPI.logout());
    }
}

/**
 * Display admin name in header
 */
function displayAdminName() {
    const nameEl = document.getElementById('adminName');
    if (nameEl) {
        const user = AdminAPI.getUser();
        if (user) nameEl.textContent = user.username;
    }
}
