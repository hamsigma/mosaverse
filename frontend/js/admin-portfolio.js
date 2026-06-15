/**
 * Admin Portfolio Management
 */

AdminAPI.requireAuth();
setupLogout();

let portfolios = [];
let currentPortfolioId = null;

// ─── Load Portfolios ────────────────────────────────────

async function loadPortfolios() {
    try {
        const data = await AdminAPI.getPortfolios();
        portfolios = data.results || data;
        renderPortfolioList();
    } catch (e) {
        showToast('Gagal memuat portfolio.', 'error');
    }
}

function renderPortfolioList() {
    const list = document.getElementById('portfolioList');
    const empty = document.getElementById('emptyState');

    if (portfolios.length === 0) {
        list.innerHTML = '';
        empty.classList.remove('hidden');
        return;
    }

    empty.classList.add('hidden');
    list.innerHTML = portfolios.map(p => {
        const firstImg = p.images && p.images.length > 0 ? p.images[0].image_url : null;
        const thumbUrl = p.thumbnail_url || firstImg || 'https://via.placeholder.com/300x200?text=No+Thumbnail';
        const imgCount = p.image_count || 0;
        return `
            <div class="bg-white rounded-2xl shadow-sm overflow-hidden hover:shadow-md transition-shadow">
                <div class="aspect-[3/2] overflow-hidden bg-gray-100">
                    <img src="${thumbUrl}" alt="${p.title}" class="w-full h-full object-cover">
                </div>
                <div class="p-5">
                    <h3 class="font-epilogue text-base font-bold text-primary truncate">${p.title}</h3>
                    <p class="text-xs text-primary/40 mt-1">${imgCount} gambar</p>
                    <p class="text-sm text-primary/50 mt-2 line-clamp-2">${p.description || 'Tidak ada deskripsi.'}</p>
                    <div class="flex gap-2 mt-4">
                        <button onclick="openImageModal(${p.id})" class="flex-1 py-2 bg-primary text-accent text-[10px] font-bold uppercase tracking-widest rounded-btn hover:bg-primary/80 transition-colors">
                            Kelola Gambar
                        </button>
                        <button onclick="editPortfolio(${p.id})" class="p-2 text-primary/40 hover:text-highlight transition-colors" title="Edit">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>
                        </button>
                        <button onclick="deletePortfolio(${p.id})" class="p-2 text-primary/40 hover:text-red-500 transition-colors" title="Hapus">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                        </button>
                    </div>
                </div>
            </div>`;
    }).join('');
}

// ─── Create / Edit Modal ────────────────────────────────

function showCreateForm() {
    document.getElementById('modalTitle').textContent = 'Tambah Portfolio';
    document.getElementById('editId').value = '';
    document.getElementById('inputTitle').value = '';
    document.getElementById('inputDesc').value = '';
    document.getElementById('inputOrder').value = '0';
    document.getElementById('inputThumbnail').value = '';
    document.getElementById('thumbnailPreview').classList.add('hidden');
    document.getElementById('portfolioModal').classList.remove('hidden');
}

function editPortfolio(id) {
    const p = portfolios.find(x => x.id === id);
    if (!p) return;
    document.getElementById('modalTitle').textContent = 'Edit Portfolio';
    document.getElementById('editId').value = id;
    document.getElementById('inputTitle').value = p.title;
    document.getElementById('inputDesc').value = p.description || '';
    document.getElementById('inputOrder').value = p.order || 0;
    document.getElementById('inputThumbnail').value = '';

    const preview = document.getElementById('thumbnailPreview');
    if (p.thumbnail_url) {
        preview.src = p.thumbnail_url;
        preview.classList.remove('hidden');
    } else {
        preview.classList.add('hidden');
    }

    document.getElementById('portfolioModal').classList.remove('hidden');
}

function closeModal() {
    document.getElementById('portfolioModal').classList.add('hidden');
}

// Thumbnail preview
document.getElementById('inputThumbnail').addEventListener('change', function () {
    const preview = document.getElementById('thumbnailPreview');
    if (this.files && this.files[0]) {
        preview.src = URL.createObjectURL(this.files[0]);
        preview.classList.remove('hidden');
    }
});

// Form submit
document.getElementById('portfolioForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const editId = document.getElementById('editId').value;
    const title = document.getElementById('inputTitle').value.trim();
    const desc = document.getElementById('inputDesc').value.trim();
    const order = document.getElementById('inputOrder').value;
    const thumbFile = document.getElementById('inputThumbnail').files[0];

    if (!title) { showToast('Judul wajib diisi.', 'error'); return; }

    const formData = new FormData();
    formData.append('title', title);
    formData.append('description', desc);
    formData.append('order', order || '0');
    if (thumbFile) formData.append('thumbnail', thumbFile);

    try {
        if (editId) {
            await AdminAPI.updatePortfolio(editId, formData);
            showToast('Portfolio berhasil diupdate!');
        } else {
            await AdminAPI.createPortfolio(formData);
            showToast('Portfolio berhasil dibuat!');
        }
        closeModal();
        loadPortfolios();
    } catch (e) {
        showToast('Gagal menyimpan portfolio.', 'error');
    }
});

// ─── Delete Portfolio ───────────────────────────────────

async function deletePortfolio(id) {
    const p = portfolios.find(x => x.id === id);
    if (!p) return;
    if (!confirm(`Hapus portfolio "${p.title}"? Semua gambar di dalamnya juga akan terhapus.`)) return;

    try {
        await AdminAPI.deletePortfolio(id);
        showToast('Portfolio berhasil dihapus.');
        loadPortfolios();
    } catch (e) {
        showToast('Gagal menghapus portfolio.', 'error');
    }
}

// ─── Image Management Modal ─────────────────────────────

async function openImageModal(id) {
    currentPortfolioId = id;
    const p = portfolios.find(x => x.id === id);
    if (!p) return;

    document.getElementById('imageModalTitle').textContent = `Gambar: ${p.title}`;
    document.getElementById('inputImages').value = '';
    document.getElementById('imageModal').classList.remove('hidden');

    renderImageGrid(p.images || []);
}

function closeImageModal() {
    document.getElementById('imageModal').classList.add('hidden');
    currentPortfolioId = null;
}

function renderImageGrid(images) {
    const grid = document.getElementById('imageGrid');
    if (images.length === 0) {
        grid.innerHTML = '<p class="col-span-full text-center text-sm text-primary/40 py-8">Belum ada gambar. Upload gambar pertama.</p>';
        return;
    }
    grid.innerHTML = images.map(img => `
        <div class="relative group aspect-[4/5] rounded-xl overflow-hidden bg-gray-100">
            <img src="${img.image_url}" alt="${img.caption || ''}" class="w-full h-full object-cover">
            <div class="absolute inset-0 bg-black/0 group-hover:bg-black/40 transition-colors flex items-center justify-center">
                <button onclick="deleteImage(${img.id})" class="opacity-0 group-hover:opacity-100 p-2 bg-red-500 text-white rounded-full transition-opacity" title="Hapus gambar">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                </button>
            </div>
        </div>
    `).join('');
}

// ─── Upload Images ──────────────────────────────────────

async function uploadImages() {
    if (!currentPortfolioId) return;
    const files = document.getElementById('inputImages').files;
    if (!files || files.length === 0) {
        showToast('Pilih gambar terlebih dahulu.', 'error');
        return;
    }

    const total = files.length;
    let successCount = 0;
    const failedFiles = [];

    // Show loading state
    const uploadBtn = document.querySelector('#imageModal button[onclick="uploadImages()"]');
    const originalText = uploadBtn ? uploadBtn.textContent : '';
    if (uploadBtn) { uploadBtn.disabled = true; uploadBtn.textContent = 'Uploading...'; }

    for (const file of files) {
        const formData = new FormData();
        formData.append('image', file);
        try {
            await AdminAPI.addPortfolioImage(currentPortfolioId, formData);
            successCount++;
        } catch (e) {
            console.error('Failed to upload:', file.name, e);
            failedFiles.push(file.name);
        }
    }

    // Restore button
    if (uploadBtn) { uploadBtn.disabled = false; uploadBtn.textContent = originalText; }

    if (failedFiles.length > 0) {
        showToast(`${successCount}/${total} berhasil. Gagal: ${failedFiles.join(', ')}`, 'error');
    } else {
        showToast(`${successCount}/${total} gambar berhasil diupload.`);
    }
    document.getElementById('inputImages').value = '';

    // Refresh image grid
    const p = portfolios.find(x => x.id === currentPortfolioId);
    if (p) {
        try {
            const updated = await AdminAPI.getPortfolios();
            const updatedList = updated.results || updated;
            portfolios = updatedList;
            const fresh = updatedList.find(x => x.id === currentPortfolioId);
            if (fresh) {
                p.images = fresh.images;
                p.image_count = fresh.image_count;
                renderImageGrid(fresh.images || []);
            }
            renderPortfolioList();
        } catch (e) {
            console.error('Failed to refresh:', e);
        }
    }
}

// ─── Delete Image ───────────────────────────────────────

async function deleteImage(imageId) {
    if (!confirm('Hapus gambar ini?')) return;

    try {
        await AdminAPI.deletePortfolioImage(imageId);
        showToast('Gambar berhasil dihapus.');

        // Refresh
        const updated = await AdminAPI.getPortfolios();
        portfolios = updated.results || updated;
        if (currentPortfolioId) {
            const fresh = portfolios.find(x => x.id === currentPortfolioId);
            if (fresh) renderImageGrid(fresh.images || []);
        }
        renderPortfolioList();
    } catch (e) {
        showToast('Gagal menghapus gambar.', 'error');
    }
}

// ─── Expose functions globally ──────────────────────────
window.showCreateForm = showCreateForm;
window.closeModal = closeModal;
window.editPortfolio = editPortfolio;
window.deletePortfolio = deletePortfolio;
window.openImageModal = openImageModal;
window.closeImageModal = closeImageModal;
window.uploadImages = uploadImages;
window.deleteImage = deleteImage;

// ─── Init ───────────────────────────────────────────────
loadPortfolios();
