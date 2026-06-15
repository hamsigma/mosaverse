/**
 * Admin Login Page Logic
 */

// If already logged in, redirect to dashboard
if (AdminAPI.isAuthenticated()) {
    window.location.href = 'admin-dashboard.html';
}

const loginForm = document.getElementById('loginForm');
const errorMsg = document.getElementById('errorMsg');
const loginBtn = document.getElementById('loginBtn');

loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    errorMsg.classList.add('hidden');
    loginBtn.disabled = true;
    loginBtn.innerHTML = 'Signing in...';

    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;

    try {
        const result = await AdminAPI.login(username, password);
        window.location.href = 'admin-dashboard.html';
    } catch (error) {
        console.error('Login error:', error);
        errorMsg.textContent = 'Username atau password salah.';
        errorMsg.classList.remove('hidden');
    } finally {
        loginBtn.disabled = false;
        loginBtn.innerHTML = 'Login to Dashboard <svg class="w-4 h-4 inline-block" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>';
    }
});
