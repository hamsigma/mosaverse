/**
 * Admin Dashboard Logic
 */

AdminAPI.requireAuth();
setupLogout();

// Show logged-in admin username
const user = AdminAPI.getUser();
if (user && user.username) {
    document.getElementById('adminUsername').textContent = user.username;
}

function formatNumber(num) {
    if (num >= 1000) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }
    return num.toString();
}

async function loadDashboard() {
    try {
        const data = await AdminAPI.getStats();
        const stats = data.stats || {};

        document.getElementById('statTotalDesigns').textContent = formatNumber(stats.total_designs || 0);
        document.getElementById('statPublished').textContent = formatNumber(stats.published_designs || 0);
        document.getElementById('statPending').textContent = formatNumber(stats.pending_designs || 0);
        document.getElementById('statTotalCategories').textContent = formatNumber(stats.total_categories || 0);

        // Recent designs
        const tbody = document.getElementById('recentDesigns');
        const recentDesigns = data.recent_designs || [];

        if (recentDesigns.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="4" class="px-6 py-8 text-center text-sm text-primary/40">
                        Belum ada desain. <a href="admin-designs.html" class="text-highlight hover:underline">Tambah desain baru</a>
                    </td>
                </tr>`;
        } else {
            tbody.innerHTML = recentDesigns.map(d => {
                const imageUrl = d.image_url || 'https://via.placeholder.com/48?text=?';
                const statusLabel = d.is_published ? 'APPROVED' : 'PENDING';
                const statusClass = d.is_published
                    ? 'bg-primary text-accent'
                    : 'bg-primary/10 text-primary/60';
                const dateStr = formatDate(d.created_at);
                const category = d.category_name || 'Uncategorized';

                return `
                    <tr class="border-t border-primary/5 hover:bg-primary/[0.02] transition-colors cursor-pointer"
                        onclick="window.location.href='admin-designs.html'">
                        <td class="px-6 py-3">
                            <div class="flex items-center gap-3">
                                <div class="w-10 h-10 rounded-btn overflow-hidden bg-primary/5 flex-shrink-0">
                                    <img src="${imageUrl}" alt="${d.title}" class="w-full h-full object-cover">
                                </div>
                                <span class="text-sm font-semibold truncate max-w-[200px]">${d.title}</span>
                            </div>
                        </td>
                        <td class="px-6 py-3 text-sm text-primary/60">${category}</td>
                        <td class="px-6 py-3">
                            <span class="px-3 py-1 text-[10px] font-bold uppercase tracking-wider rounded-full ${statusClass}">
                                ${statusLabel}
                            </span>
                        </td>
                        <td class="px-6 py-3 text-sm text-primary/60">${dateStr}</td>
                    </tr>`;
            }).join('');
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

loadDashboard();
