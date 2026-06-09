/**
 * Admin Dashboard Logic
 */

AdminAPI.requireAuth();
setupLogout();
displayAdminName();

async function loadDashboard() {
    try {
        const data = await AdminAPI.getStats();
        const stats = data.stats || {};

        document.getElementById('statTotalDesigns').textContent = stats.total_designs || 0;
        document.getElementById('statTotalCategories').textContent = stats.total_categories || 0;
        document.getElementById('statFeatured').textContent = stats.featured_designs || 0;
        document.getElementById('statPublished').textContent = stats.published_designs || 0;

        // Recent designs
        const recentContainer = document.getElementById('recentDesigns');
        const recentDesigns = data.recent_designs || [];

        if (recentDesigns.length === 0) {
            recentContainer.innerHTML = '<div class="px-6 py-8 text-center text-sm text-primary/40">Belum ada desain.</div>';
        } else {
            recentContainer.innerHTML = recentDesigns.map(d => {
                const imageUrl = d.image_url || 'https://via.placeholder.com/48x64?text=?';
                return `
                    <a href="admin-design-form.html?id=${d.id}" class="flex items-center gap-4 px-6 py-3 hover:bg-primary/3 transition-colors">
                        <div class="w-12 h-16 rounded-btn overflow-hidden bg-primary/5 flex-shrink-0">
                            <img src="${imageUrl}" alt="${d.title}" class="w-full h-full object-cover">
                        </div>
                        <div class="flex-1 min-w-0">
                            <p class="text-sm font-semibold truncate">${d.title}</p>
                            <p class="text-xs text-primary/40">${d.category_name || 'No category'} &middot; ${formatDate(d.created_at)}</p>
                        </div>
                        ${d.is_featured ? '<span class="px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-highlight bg-highlight/10 rounded-full">Featured</span>' : ''}
                    </a>
                `;
            }).join('');
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

loadDashboard();
