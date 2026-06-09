/**
 * Admin Designs Management Logic
 */

AdminAPI.requireAuth();
setupLogout();

let currentPage = 1;
let deleteTargetId = null;

const tableBody = document.getElementById('designsTableBody');
const paginationPages = document.getElementById('designsPages');
const designsInfo = document.getElementById('designsInfo');

/**
 * Load designs into the table
 */
async function loadDesigns(page = 1) {
    currentPage = page;
    tableBody.innerHTML = '<tr><td colspan="5" class="px-6 py-12 text-center text-sm text-primary/40">Loading...</td></tr>';

    try {
        // Use a higher limit for admin to see all designs
        const url = new URL(`${API_BASE}/designs/`);
        url.searchParams.set('page', page);
        // Admin needs to see all designs, not just published
        const response = await fetch(url, { credentials: 'include' });
        const data = await response.json();

        const designs = data.results || [];

        if (designs.length === 0) {
            tableBody.innerHTML = `
                <tr><td colspan="5" class="px-6 py-12 text-center">
                    <p class="text-sm text-primary/40">Belum ada desain.</p>
                    <a href="admin-design-form.html" class="inline-block mt-3 text-sm text-highlight font-semibold hover:underline">+ Tambah desain pertama</a>
                </td></tr>`;
            return;
        }

        tableBody.innerHTML = designs.map(d => {
            const imageUrl = d.image_url || 'https://via.placeholder.com/48x64?text=?';
            const statusBadges = [];
            if (d.is_featured) statusBadges.push('<span class="px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-highlight bg-highlight/10 rounded-full">Featured</span>');
            if (d.category_name) statusBadges.push(`<span class="px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-primary/60 bg-primary/5 rounded-full">${d.category_name}</span>`);

            return `
                <tr class="border-b border-primary/5 hover:bg-primary/3 transition-colors">
                    <td class="px-6 py-3">
                        <div class="flex items-center gap-3">
                            <div class="w-12 h-16 rounded-btn overflow-hidden bg-primary/5 flex-shrink-0">
                                <img src="${imageUrl}" alt="${d.title}" class="w-full h-full object-cover">
                            </div>
                            <div>
                                <p class="text-sm font-semibold">${d.title}</p>
                                <p class="text-xs text-primary/40 truncate max-w-[200px]">${d.description || ''}</p>
                            </div>
                        </div>
                    </td>
                    <td class="px-6 py-3">
                        ${d.category_name ? `<span class="px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-primary/60 bg-primary/5 rounded-full">${d.category_name}</span>` : '<span class="text-xs text-primary/30">-</span>'}
                    </td>
                    <td class="px-6 py-3">
                        <div class="flex items-center gap-1.5">
                            ${d.is_featured ? '<span class="px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-highlight bg-highlight/10 rounded-full">Featured</span>' : ''}
                            <span class="px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-green-700 bg-green-50 rounded-full">Published</span>
                        </div>
                    </td>
                    <td class="px-6 py-3 text-xs text-primary/50">${formatDate(d.created_at)}</td>
                    <td class="px-6 py-3 text-right">
                        <div class="flex items-center justify-end gap-2">
                            <a href="admin-design-form.html?id=${d.id}" class="p-2 text-primary/40 hover:text-highlight transition-colors" title="Edit">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>
                            </a>
                            <button onclick="openDeleteModal(${d.id}, '${d.title.replace(/'/g, "\\'")}')" class="p-2 text-primary/40 hover:text-red-600 transition-colors" title="Delete">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');

        // Pagination
        const totalCount = data.count || 0;
        const totalPages = Math.ceil(totalCount / 12);
        const startItem = (page - 1) * 12 + 1;
        const endItem = Math.min(page * 12, totalCount);

        designsInfo.textContent = `Showing ${startItem}-${endItem} of ${totalCount} designs`;

        let pagesHtml = '';
        if (totalPages > 1) {
            pagesHtml += `<button class="page-btn" ${page === 1 ? 'disabled' : ''} onclick="loadDesigns(${page - 1})"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg></button>`;
            for (let i = 1; i <= totalPages; i++) {
                pagesHtml += `<button class="page-btn ${i === page ? 'active' : ''}" onclick="loadDesigns(${i})">${i}</button>`;
            }
            pagesHtml += `<button class="page-btn" ${page === totalPages ? 'disabled' : ''} onclick="loadDesigns(${page + 1})"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg></button>`;
        }
        paginationPages.innerHTML = pagesHtml;

    } catch (error) {
        console.error('Error loading designs:', error);
        tableBody.innerHTML = '<tr><td colspan="5" class="px-6 py-12 text-center text-sm text-red-500">Error loading designs.</td></tr>';
    }
}

/**
 * Open delete confirmation modal
 */
function openDeleteModal(id, name) {
    deleteTargetId = id;
    document.getElementById('deleteDesignName').textContent = name;
    document.getElementById('deleteModal').classList.remove('hidden');
}

/**
 * Close delete modal
 */
function closeDeleteModal() {
    deleteTargetId = null;
    document.getElementById('deleteModal').classList.add('hidden');
}

// Confirm delete
document.getElementById('confirmDeleteBtn').addEventListener('click', async () => {
    if (!deleteTargetId) return;

    const btn = document.getElementById('confirmDeleteBtn');
    btn.disabled = true;
    btn.textContent = 'Deleting...';

    try {
        await AdminAPI.deleteDesign(deleteTargetId);
        closeDeleteModal();
        showToast('Design berhasil dihapus.');
        loadDesigns(currentPage);
    } catch (error) {
        console.error('Error deleting design:', error);
        showToast('Gagal menghapus design.', 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Delete';
    }
});

// Initialize
loadDesigns();
