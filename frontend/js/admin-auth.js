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
    loginBtn.textContent = 'Signing in...';

    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;

    try {
        await AdminAPI.login(username, password);
        window.location.href = 'admin-dashboard.html';
    } catch (error) {
        console.error('Login error:', error);
        errorMsg.textContent = 'Username atau password salah.';
        errorMsg.classList.remove('hidden');
    } finally {
        loginBtn.disabled = false;
        loginBtn.textContent = 'Sign In';
    }
});
