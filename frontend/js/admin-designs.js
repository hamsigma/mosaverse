/**
 * Admin Designs — Combined Form + Catalog (Kelola Desain)
 */

AdminAPI.requireAuth();
setupLogout();

// ─── State ─────────────────────────────────────────────
let currentPage = 1;
let deleteTargetId = null;
let selectedImageFile = null;
let editingId = null;
let searchTimeout = null;

// ─── DOM Elements ──────────────────────────────────────
const form = document.getElementById('designForm');
const formTitle = document.getElementById('formTitle');
const saveBtn = document.getElementById('saveBtn');
const titleInput = document.getElementById('title');
const descriptionInput = document.getElementById('description');
const categorySelect = document.getElementById('category');
const imageInput = document.getElementById('imageInput');
const imageUploadArea = document.getElementById('imageUploadArea');
const imagePreview = document.getElementById('imagePreview');
const previewImg = document.getElementById('previewImg');
const uploadPlaceholder = document.getElementById('uploadPlaceholder');
const removeImageBtn = document.getElementById('removeImageBtn');
const tableBody = document.getElementById('designsTableBody');
const paginationPages = document.getElementById('designsPages');
const designsInfo = document.getElementById('designsInfo');
const searchInput = document.getElementById('searchInput');

// ─── Categories ────────────────────────────────────────
async function loadCategories() {
    try {
        const data = await API.getCategories();
        const categories = data.results || data || [];
        categorySelect.innerHTML = '<option value="">Pilih atau ketik kategori...</option>';
        categories.forEach(cat => {
            const opt = document.createElement('option');
            opt.value = cat.id;
            opt.textContent = cat.name;
            categorySelect.appendChild(opt);
        });
    } catch (e) {
        console.error('Error loading categories:', e);
    }
}

// ─── Image Upload ──────────────────────────────────────
imageUploadArea.addEventListener('click', (e) => {
    if (e.target.id === 'removeImageBtn' || e.target.closest('#removeImageBtn')) return;
    imageInput.click();
});

imageInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) showImagePreview(file);
});

function showImagePreview(file) {
    selectedImageFile = file;
    const reader = new FileReader();
    reader.onload = (ev) => {
        previewImg.src = ev.target.result;
        imagePreview.classList.remove('hidden');
        uploadPlaceholder.classList.add('hidden');
    };
    reader.readAsDataURL(file);
}

removeImageBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    selectedImageFile = null;
    imageInput.value = '';
    imagePreview.classList.add('hidden');
    uploadPlaceholder.classList.remove('hidden');
    previewImg.src = '';
});

// Drag & drop
imageUploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    imageUploadArea.classList.add('border-highlight');
});
imageUploadArea.addEventListener('dragleave', () => {
    imageUploadArea.classList.remove('border-highlight');
});
imageUploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    imageUploadArea.classList.remove('border-highlight');
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
        imageInput.files = e.dataTransfer.files;
        showImagePreview(file);
    }
});

// ─── AI Generate Description ───────────────────────────
document.getElementById('generateDescBtn').addEventListener('click', async () => {
    const title = titleInput.value.trim();
    if (!title) { showToast('Isi nama desain terlebih dahulu.', 'error'); return; }

    const catText = categorySelect.options[categorySelect.selectedIndex]?.text || '';
    const loading = document.getElementById('descLoading');
    const btn = document.getElementById('generateDescBtn');

    loading.classList.remove('hidden');
    btn.disabled = true;
    try {
        const data = await AdminAPI.generateDescription(title, catText, editingId || null);
        descriptionInput.value = data.description || '';
        showToast('Deskripsi berhasil di-generate!');
    } catch (e) {
        showToast('Gagal generate deskripsi.', 'error');
    } finally {
        loading.classList.add('hidden');
        btn.disabled = false;
    }
});

// ─── AI Generate Category ──────────────────────────────
document.getElementById('generateCategoryBtn').addEventListener('click', async () => {
    const title = titleInput.value.trim();
    if (!title) { showToast('Isi nama desain terlebih dahulu.', 'error'); return; }

    const desc = descriptionInput.value.trim();
    const loading = document.getElementById('categoryLoading');
    const btn = document.getElementById('generateCategoryBtn');

    loading.classList.remove('hidden');
    btn.disabled = true;
    try {
        const data = await AdminAPI.generateCategory(title, desc, editingId || null);
        await loadCategories();
        categorySelect.value = data.category_id;
        showToast(`Kategori "${data.category}" berhasil ditentukan!`);
    } catch (e) {
        showToast('Gagal generate kategori.', 'error');
    } finally {
        loading.classList.add('hidden');
        btn.disabled = false;
    }
});

// ─── Form Submit ───────────────────────────────────────
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    saveBtn.disabled = true;
    saveBtn.textContent = editingId ? 'Mengupdate...' : 'Menyimpan...';

    try {
        const formData = new FormData();
        formData.append('title', titleInput.value.trim());
        formData.append('description', descriptionInput.value.trim());
        formData.append('is_featured', 'false');
        formData.append('is_published', 'true');

        if (categorySelect.value) formData.append('category_id', categorySelect.value);

        if (selectedImageFile) {
            formData.append('image', selectedImageFile);
        } else if (!editingId) {
            showToast('Upload gambar desain.', 'error');
            saveBtn.disabled = false;
            saveBtn.innerHTML = '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"/></svg> Simpan Desain';
            return;
        }

        if (editingId) {
            await AdminAPI.updateDesign(editingId, formData);
            showToast('Desain berhasil diupdate!');
        } else {
            await AdminAPI.createDesign(formData);
            showToast('Desain berhasil dibuat!');
        }

        resetForm();
        loadDesigns(currentPage);
    } catch (e) {
        console.error('Save error:', e);
        const msg = e.message || '';
        if (msg.includes('image') || msg.includes('No file')) {
            showToast('Upload gambar desain untuk melanjutkan.', 'error');
        } else {
            showToast('Gagal menyimpan desain. Periksa kembali form Anda.', 'error');
        }
    } finally {
        saveBtn.disabled = false;
        saveBtn.innerHTML = '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"/></svg> Simpan Desain';
    }
});

// ─── Reset Form ────────────────────────────────────────
function resetForm() {
    editingId = null;
    form.reset();
    selectedImageFile = null;
    imageInput.value = '';
    imagePreview.classList.add('hidden');
    uploadPlaceholder.classList.remove('hidden');
    previewImg.src = '';
    formTitle.textContent = 'Tambah / Edit Desain';
}

// ─── Load Design for Editing ───────────────────────────
async function editDesign(id) {
    try {
        const d = await API.getDesign(id);
        editingId = id;
        formTitle.textContent = 'Edit Desain';
        titleInput.value = d.title || '';
        descriptionInput.value = d.description || '';

        if (d.category) categorySelect.value = d.category.id;

        if (d.image_url || d.image) {
            previewImg.src = d.image_url || d.image;
            imagePreview.classList.remove('hidden');
            uploadPlaceholder.classList.add('hidden');
        }

        // Scroll form into view
        form.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } catch (e) {
        showToast('Gagal memuat data desain.', 'error');
    }
}

// ─── Catalog: Load Designs ─────────────────────────────
async function loadDesigns(page = 1, search = '') {
    currentPage = page;
    tableBody.innerHTML = '<tr><td colspan="4" class="px-6 py-12 text-center text-sm text-primary/40">Loading...</td></tr>';

    try {
        const data = await API.get('/designs/', { page, admin: 1, ...(search && { search }) });
        const designs = data.results || [];

        if (designs.length === 0) {
            tableBody.innerHTML = `
                <tr><td colspan="4" class="px-6 py-12 text-center">
                    <p class="text-sm text-primary/40">Belum ada desain.</p>
                </td></tr>`;
            designsInfo.textContent = '0 desain';
            paginationPages.innerHTML = '';
            return;
        }

        tableBody.innerHTML = designs.map(d => {
            const imageUrl = d.image_url || 'https://via.placeholder.com/48?text=?';
            const catName = d.category_name || '—';
            const isDraft = !d.is_published;
            const dateStr = formatDate(d.created_at);

            return `
                <tr class="border-b border-primary/5 hover:bg-primary/[0.02] transition-colors">
                    <td class="px-6 py-3">
                        <div class="w-12 h-12 rounded-btn overflow-hidden bg-primary/5 flex-shrink-0">
                            <img src="${imageUrl}" alt="${d.title}" class="w-full h-full object-cover">
                        </div>
                    </td>
                    <td class="px-6 py-3">
                        <p class="text-sm font-semibold">${d.title}</p>
                        <p class="text-[11px] text-primary/40 mt-0.5">${isDraft ? 'Draft' : 'Ditambahkan'} ${dateStr}</p>
                    </td>
                    <td class="px-6 py-3">
                        <span class="px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-accent bg-primary rounded-full">${catName}</span>
                    </td>
                    <td class="px-6 py-3 text-right">
                        <div class="flex items-center justify-end gap-1">
                            <button onclick="editDesign(${d.id})" class="p-2 text-primary/40 hover:text-highlight transition-colors" title="Edit">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>
                            </button>
                            <button onclick="openDeleteModal(${d.id}, '${d.title.replace(/'/g, "\\'")}')" class="p-2 text-primary/40 hover:text-red-600 transition-colors" title="Hapus">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                            </button>
                        </div>
                    </td>
                </tr>`;
        }).join('');

        // Pagination
        const totalCount = data.count || 0;
        const totalPages = Math.ceil(totalCount / 12);
        const startItem = (page - 1) * 12 + 1;
        const endItem = Math.min(page * 12, totalCount);
        designsInfo.textContent = `${startItem}–${endItem} dari ${totalCount} desain`;

        let pagesHtml = '';
        if (totalPages > 1) {
            pagesHtml += `<button class="page-btn" ${page === 1 ? 'disabled' : ''} onclick="loadDesigns(${page - 1}, document.getElementById('searchInput').value)"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg></button>`;
            for (let i = 1; i <= totalPages; i++) {
                pagesHtml += `<button class="page-btn ${i === page ? 'active' : ''}" onclick="loadDesigns(${i}, document.getElementById('searchInput').value)">${i}</button>`;
            }
            pagesHtml += `<button class="page-btn" ${page === totalPages ? 'disabled' : ''} onclick="loadDesigns(${page + 1}, document.getElementById('searchInput').value)"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg></button>`;
        }
        paginationPages.innerHTML = pagesHtml;

    } catch (e) {
        console.error('Error loading designs:', e);
        tableBody.innerHTML = '<tr><td colspan="4" class="px-6 py-12 text-center text-sm text-red-500">Gagal memuat desain.</td></tr>';
    }
}

// ─── Search ────────────────────────────────────────────
searchInput.addEventListener('input', (e) => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        loadDesigns(1, e.target.value.trim());
    }, 400);
});

// ─── Delete Modal ──────────────────────────────────────
function openDeleteModal(id, name) {
    deleteTargetId = id;
    document.getElementById('deleteDesignName').textContent = name;
    document.getElementById('deleteModal').classList.remove('hidden');
}

function closeDeleteModal() {
    deleteTargetId = null;
    document.getElementById('deleteModal').classList.add('hidden');
}

document.getElementById('confirmDeleteBtn').addEventListener('click', async () => {
    if (!deleteTargetId) return;
    const btn = document.getElementById('confirmDeleteBtn');
    btn.disabled = true;
    btn.textContent = 'Menghapus...';

    try {
        await AdminAPI.deleteDesign(deleteTargetId);
        closeDeleteModal();
        showToast('Desain berhasil dihapus.');
        if (editingId == deleteTargetId) resetForm();
        loadDesigns(currentPage, searchInput.value.trim());
    } catch (e) {
        showToast('Gagal menghapus desain.', 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Hapus';
    }
});

// ─── Initialize ────────────────────────────────────────
loadCategories();
loadDesigns();
