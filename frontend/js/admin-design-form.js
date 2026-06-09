/**
 * Admin Design Form — Add/Edit with AI Integration
 */

AdminAPI.requireAuth();
setupLogout();

const designId = getUrlParam('id');
const isEdit = !!designId;
const formTitle = document.getElementById('formTitle');
const designForm = document.getElementById('designForm');
const saveBtn = document.getElementById('saveBtn');

// Elements
const titleInput = document.getElementById('title');
const descriptionInput = document.getElementById('description');
const categorySelect = document.getElementById('category');
const isFeaturedInput = document.getElementById('isFeatured');
const isPublishedInput = document.getElementById('isPublished');
const imageInput = document.getElementById('imageInput');
const imagePreview = document.getElementById('imagePreview');
const previewImg = document.getElementById('previewImg');
const uploadPlaceholder = document.getElementById('uploadPlaceholder');
const imageUploadArea = document.getElementById('imageUploadArea');

let selectedImageFile = null;

/**
 * Load categories into select
 */
async function loadCategories() {
    try {
        const data = await API.getCategories();
        const categories = data.results || data || [];
        categories.forEach(cat => {
            const option = document.createElement('option');
            option.value = cat.id;
            option.textContent = cat.name;
            categorySelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

/**
 * Load existing design for editing
 */
async function loadDesign() {
    if (!isEdit) return;

    formTitle.textContent = 'Edit Design';
    document.title = 'MosaVerse Admin — Edit Design';
    saveBtn.textContent = 'Update Design';

    try {
        const design = await API.getDesign(designId);
        titleInput.value = design.title || '';
        descriptionInput.value = design.description || '';
        isFeaturedInput.checked = design.is_featured || false;
        isPublishedInput.checked = design.is_published !== false;

        if (design.category) {
            categorySelect.value = design.category.id;
        }

        if (design.image_url || design.image) {
            previewImg.src = design.image_url || design.image;
            imagePreview.classList.remove('hidden');
            uploadPlaceholder.classList.add('hidden');
        }

        document.getElementById('designId').value = design.id;
    } catch (error) {
        console.error('Error loading design:', error);
        showToast('Gagal memuat data design.', 'error');
    }
}

/**
 * Image upload handling
 */
imageUploadArea.addEventListener('click', () => imageInput.click());

imageInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        selectedImageFile = file;
        const reader = new FileReader();
        reader.onload = (ev) => {
            previewImg.src = ev.target.result;
            imagePreview.classList.remove('hidden');
            uploadPlaceholder.classList.add('hidden');
        };
        reader.readAsDataURL(file);
    }
});

// Drag and drop
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
        selectedImageFile = file;
        imageInput.files = e.dataTransfer.files;
        const reader = new FileReader();
        reader.onload = (ev) => {
            previewImg.src = ev.target.result;
            imagePreview.classList.remove('hidden');
            uploadPlaceholder.classList.add('hidden');
        };
        reader.readAsDataURL(file);
    }
});

/**
 * AI Generate Description
 */
document.getElementById('generateDescBtn').addEventListener('click', async () => {
    const title = titleInput.value.trim();
    if (!title) {
        showToast('Isi title terlebih dahulu.', 'error');
        return;
    }

    const categoryText = categorySelect.options[categorySelect.selectedIndex]?.text || '';
    const loading = document.getElementById('descLoading');
    const btn = document.getElementById('generateDescBtn');

    loading.classList.remove('hidden');
    btn.disabled = true;

    try {
        const data = await AdminAPI.generateDescription(title, categoryText, designId || null);
        descriptionInput.value = data.description || '';
        showToast('Deskripsi berhasil di-generate!');
    } catch (error) {
        console.error('AI error:', error);
        showToast('Gagal generate deskripsi.', 'error');
    } finally {
        loading.classList.add('hidden');
        btn.disabled = false;
    }
});

/**
 * AI Generate Category
 */
document.getElementById('generateCategoryBtn').addEventListener('click', async () => {
    const title = titleInput.value.trim();
    if (!title) {
        showToast('Isi title terlebih dahulu.', 'error');
        return;
    }

    const description = descriptionInput.value.trim();
    const loading = document.getElementById('categoryLoading');
    const btn = document.getElementById('generateCategoryBtn');

    loading.classList.remove('hidden');
    btn.disabled = true;

    try {
        const data = await AdminAPI.generateCategory(title, description, designId || null);
        // Reload categories and select the new one
        await loadCategories();
        categorySelect.value = data.category_id;
        showToast(`Kategori "${data.category}" berhasil ditentukan!`);
    } catch (error) {
        console.error('AI error:', error);
        showToast('Gagal generate kategori.', 'error');
    } finally {
        loading.classList.add('hidden');
        btn.disabled = false;
    }
});

/**
 * Save design (create or update)
 */
designForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    saveBtn.disabled = true;
    saveBtn.textContent = isEdit ? 'Updating...' : 'Saving...';

    try {
        const formData = new FormData();
        formData.append('title', titleInput.value.trim());
        formData.append('description', descriptionInput.value.trim());
        formData.append('is_featured', isFeaturedInput.checked);
        formData.append('is_published', isPublishedInput.checked);

        if (categorySelect.value) {
            formData.append('category_id', categorySelect.value);
        }

        if (selectedImageFile) {
            formData.append('image', selectedImageFile);
        } else if (!isEdit) {
            showToast('Upload gambar design.', 'error');
            saveBtn.disabled = false;
            saveBtn.textContent = 'Save Design';
            return;
        }

        if (isEdit) {
            await AdminAPI.updateDesign(designId, formData);
            showToast('Design berhasil diupdate!');
        } else {
            await AdminAPI.createDesign(formData);
            showToast('Design berhasil dibuat!');
        }

        setTimeout(() => {
            window.location.href = 'admin-designs.html';
        }, 1000);

    } catch (error) {
        console.error('Save error:', error);
        showToast('Gagal menyimpan design.', 'error');
        saveBtn.disabled = false;
        saveBtn.textContent = isEdit ? 'Update Design' : 'Save Design';
    }
});

// Initialize
loadCategories();
if (isEdit) loadDesign();
