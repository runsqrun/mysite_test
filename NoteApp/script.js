// 备忘录应用 - 主脚本
document.addEventListener('DOMContentLoaded', () => {
    // DOM 元素
    const notesList = document.getElementById('notesList');
    const todosList = document.getElementById('todosList');
    const noteCount = document.getElementById('noteCount');
    const searchInput = document.getElementById('searchInput');
    const addNoteBtn = document.getElementById('addNoteBtn');
    const noteModal = document.getElementById('noteModal');
    const closeModal = document.getElementById('closeModal');
    const saveNote = document.getElementById('saveNote');
    const deleteNote = document.getElementById('deleteNote');
    const toggleStar = document.getElementById('toggleStar');
    const noteTitle = document.getElementById('noteTitle');
    const noteContent = document.getElementById('noteContent');
    const noteId = document.getElementById('noteId');
    const tabs = document.querySelectorAll('.tab');
    const menuBtn = document.querySelector('.menu-btn');
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    
    // 图片上传相关
    const uploadImageBtn = document.getElementById('uploadImageBtn');
    const imageInput = document.getElementById('imageInput');
    const imagePreviewContainer = document.getElementById('imagePreviewContainer');
    
    // 编辑模式相关
    const editModeToolbar = document.getElementById('editModeToolbar');
    const selectedCountEl = document.getElementById('selectedCount');
    const selectAllBtn = document.getElementById('selectAllBtn');
    const deleteSelectedBtn = document.getElementById('deleteSelectedBtn');
    const cancelEditBtn = document.getElementById('cancelEditBtn');

    // 示例数据
    const sampleNotes = [
        {
            id: 1,
            title: '多场景联动打造"赏秋游"沉浸式新体验"…',
            content: '秋天的北京有其独特的城市气质。围绕古都文化、红色文化，推出多条特色旅游路线，让游客深度感受北京秋季的独特魅力。',
            date: '昨天',
            starred: false,
            thumbnail: 'https://images.unsplash.com/photo-1508193638397-1c4234db14d9?w=120&h=120&fit=crop'
        },
        {
            id: 2,
            title: '测试',
            content: '你自己觉得好吃不错不错哦低很多别的面对面的明白…',
            date: '昨天',
            starred: false,
            thumbnail: null
        },
        {
            id: 3,
            title: '好的接电话的好好的别的',
            content: '好的接电话的好好的别的记得记得多多',
            date: '10月29日',
            starred: true,
            thumbnail: null
        },
        {
            id: 4,
            title: '还是继续不能说',
            content: '还是继续不能说吧',
            date: '10月29日',
            starred: false,
            thumbnail: null
        },
        {
            id: 5,
            title: '八点半八点半的班',
            content: '八点半八点半的班',
            date: '10月20日',
            starred: true,
            thumbnail: null
        },
        {
            id: 6,
            title: '八点半到八点半八点半到八点半不懂',
            content: '八点半到八点半八点半到八点半不懂，继续加油努力工作。',
            date: '10月20日',
            starred: false,
            thumbnail: null
        }
    ];

    // 从 localStorage 加载数据或使用示例数据
    let notes = JSON.parse(localStorage.getItem('notes')) || sampleNotes;
    let currentTab = 'notes';
    let isStarred = false;
    let currentImages = []; // 当前编辑笔记的图片
    
    // 编辑模式状态
    let isEditMode = false;
    let selectedNotes = new Set();
    let longPressTimer = null;
    let draggedNote = null;

    // 初始化
    init();

    function init() {
        renderNotes();
        bindEvents();
    }

    // 绑定事件
    function bindEvents() {
        // 添加笔记按钮
        addNoteBtn.addEventListener('click', () => openModal());

        // 关闭模态框
        closeModal.addEventListener('click', () => closeModalHandler());

        // 保存笔记
        saveNote.addEventListener('click', () => saveNoteHandler());

        // 删除笔记
        deleteNote.addEventListener('click', () => deleteNoteHandler());

        // 切换收藏
        toggleStar.addEventListener('click', () => toggleStarHandler());

        // 搜索功能
        searchInput.addEventListener('input', (e) => filterNotes(e.target.value));

        // 标签切换
        tabs.forEach(tab => {
            tab.addEventListener('click', () => switchTab(tab.dataset.tab));
        });

        // 侧边栏
        menuBtn.addEventListener('click', () => toggleSidebar(true));
        sidebarOverlay.addEventListener('click', () => toggleSidebar(false));

        // 点击模态框外部关闭
        noteModal.addEventListener('click', (e) => {
            if (e.target === noteModal) {
                closeModalHandler();
            }
        });

        // 键盘快捷键
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !noteModal.classList.contains('hidden')) {
                closeModalHandler();
            }
        });
        
        // 图片上传事件
        uploadImageBtn.addEventListener('click', () => imageInput.click());
        imageInput.addEventListener('change', handleImageUpload);
        
        // 编辑模式事件
        selectAllBtn.addEventListener('click', selectAllNotes);
        deleteSelectedBtn.addEventListener('click', deleteSelectedNotes);
        cancelEditBtn.addEventListener('click', exitEditMode);
    }

    // 渲染笔记列表
    function renderNotes(filteredNotes = null) {
        const notesToRender = filteredNotes || notes;
        
        if (notesToRender.length === 0) {
            notesList.innerHTML = `
                <div class="empty-state">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                        <polyline points="14 2 14 8 20 8"></polyline>
                        <line x1="16" y1="13" x2="8" y2="13"></line>
                        <line x1="16" y1="17" x2="8" y2="17"></line>
                        <polyline points="10 9 9 9 8 9"></polyline>
                    </svg>
                    <p>暂无备忘</p>
                    <p style="font-size: 14px; margin-top: 8px;">点击下方按钮创建新备忘</p>
                </div>
            `;
        } else {
            notesList.innerHTML = notesToRender.map(note => createNoteCard(note)).join('');
            
            // 绑定笔记卡片点击事件
            document.querySelectorAll('.note-card').forEach(card => {
                // 长按事件（触发编辑模式）
                card.addEventListener('mousedown', (e) => handleLongPressStart(e, card));
                card.addEventListener('mouseup', () => handleLongPressEnd());
                card.addEventListener('mouseleave', () => handleLongPressEnd());
                
                // 触摸设备支持
                card.addEventListener('touchstart', (e) => handleTouchStart(e, card), { passive: false });
                card.addEventListener('touchend', (e) => handleTouchEnd(e, card));
                card.addEventListener('touchmove', (e) => handleTouchMove(e, card), { passive: false });
                
                // 点击事件（仅用于鼠标点击，触摸由touchend处理）
                let lastTouchTime = 0;
                card.addEventListener('click', (e) => {
                    // 如果刚刚有触摸事件，忽略此click（避免重复触发）
                    if (Date.now() - lastTouchTime < 500) {
                        return;
                    }
                    const id = parseInt(card.dataset.id);
                    if (isEditMode) {
                        e.preventDefault();
                        toggleNoteSelection(id, card);
                    } else {
                        openModal(id);
                    }
                });
                
                // 记录触摸时间
                card.addEventListener('touchstart', () => {
                    lastTouchTime = Date.now();
                }, { passive: true });
                
                // 拖拽事件
                card.addEventListener('dragstart', (e) => handleDragStart(e, card));
                card.addEventListener('dragend', (e) => handleDragEnd(e, card));
                card.addEventListener('dragover', (e) => handleDragOver(e, card));
                card.addEventListener('dragleave', (e) => handleDragLeave(e, card));
                card.addEventListener('drop', (e) => handleDrop(e, card));
            });
        }

        // 更新笔记数量
        noteCount.textContent = notes.length;
    }

    // 创建笔记卡片 HTML
    function createNoteCard(note) {
        // 使用 images 数组的第一张图片作为右侧缩略图
        const thumbnailSrc = (note.images && note.images.length > 0) ? note.images[0] : note.thumbnail;
        const thumbnailHtml = thumbnailSrc 
            ? `<img src="${thumbnailSrc}" alt="" class="note-card-thumbnail">` 
            : '';
        
        const starHtml = note.starred 
            ? '<span class="note-card-star">★</span>' 
            : '';
        
        const selectedClass = selectedNotes.has(note.id) ? 'selected' : '';
        const editModeClass = isEditMode ? 'edit-mode' : '';

        return `
            <div class="note-card ${editModeClass} ${selectedClass}" data-id="${note.id}" draggable="${isEditMode}">
                <div class="checkbox-wrapper">
                    <div class="note-checkbox"></div>
                </div>
                <div class="note-card-content">
                    <h3 class="note-card-title">${escapeHtml(note.title) || '无标题'}</h3>
                    <div class="note-card-meta">
                        <span class="note-card-date">${note.date}</span>
                        ${starHtml}
                    </div>
                    <p class="note-card-preview">${escapeHtml(note.content) || '无内容'}</p>
                </div>
                ${thumbnailHtml}
            </div>
        `;
    }

    // 打开模态框
    function openModal(id = null) {
        if (isEditMode) return; // 编辑模式下不打开模态框
        
        noteModal.classList.remove('hidden');
        currentImages = [];
        
        if (id) {
            // 编辑现有笔记
            const note = notes.find(n => n.id === id);
            if (note) {
                noteTitle.value = note.title;
                noteContent.value = note.content;
                noteId.value = note.id;
                isStarred = note.starred;
                currentImages = note.images || [];
                updateStarButton();
                deleteNote.style.display = 'flex';
                renderImagePreviews();
            }
        } else {
            // 创建新笔记
            noteTitle.value = '';
            noteContent.value = '';
            noteId.value = '';
            isStarred = false;
            currentImages = [];
            updateStarButton();
            deleteNote.style.display = 'none';
            renderImagePreviews();
        }

        // 自动聚焦标题输入框
        setTimeout(() => noteTitle.focus(), 100);
    }

    // 关闭模态框
    function closeModalHandler() {
        noteModal.classList.add('hidden');
        noteTitle.value = '';
        noteContent.value = '';
        noteId.value = '';
        isStarred = false;
        currentImages = [];
        imagePreviewContainer.innerHTML = '';
    }

    // 保存笔记
    function saveNoteHandler() {
        const title = noteTitle.value.trim();
        const content = noteContent.value.trim();
        const id = noteId.value;

        if (!title && !content && currentImages.length === 0) {
            closeModalHandler();
            return;
        }

        if (id) {
            // 更新现有笔记
            const index = notes.findIndex(n => n.id === parseInt(id));
            if (index !== -1) {
                notes[index].title = title;
                notes[index].content = content;
                notes[index].starred = isStarred;
                notes[index].date = formatDate(new Date());
                notes[index].images = currentImages;
            }
        } else {
            // 创建新笔记
            const newNote = {
                id: Date.now(),
                title: title || '无标题',
                content: content,
                date: formatDate(new Date()),
                starred: isStarred,
                thumbnail: null,
                images: currentImages
            };
            notes.unshift(newNote);
        }

        saveToLocalStorage();
        renderNotes();
        closeModalHandler();
    }

    // 删除笔记
    function deleteNoteHandler() {
        const id = noteId.value;
        if (id) {
            if (confirm('确定要删除这条备忘吗？')) {
                notes = notes.filter(n => n.id !== parseInt(id));
                saveToLocalStorage();
                renderNotes();
                closeModalHandler();
            }
        }
    }

    // 切换收藏状态
    function toggleStarHandler() {
        isStarred = !isStarred;
        updateStarButton();
    }

    // 更新收藏按钮状态
    function updateStarButton() {
        if (isStarred) {
            toggleStar.classList.add('starred');
        } else {
            toggleStar.classList.remove('starred');
        }
    }

    // 搜索过滤笔记
    function filterNotes(query) {
        if (!query.trim()) {
            renderNotes();
            return;
        }

        const filtered = notes.filter(note => 
            note.title.toLowerCase().includes(query.toLowerCase()) ||
            note.content.toLowerCase().includes(query.toLowerCase())
        );
        renderNotes(filtered);
    }

    // 切换标签页
    function switchTab(tab) {
        currentTab = tab;
        
        tabs.forEach(t => {
            if (t.dataset.tab === tab) {
                t.classList.add('active');
            } else {
                t.classList.remove('active');
            }
        });

        if (tab === 'notes') {
            notesList.classList.remove('hidden');
            todosList.classList.add('hidden');
            document.querySelector('.page-title').textContent = '全部备忘';
            document.querySelector('.note-count').innerHTML = `<span id="noteCount">${notes.length}</span> 条备忘`;
        } else {
            notesList.classList.add('hidden');
            todosList.classList.remove('hidden');
            document.querySelector('.page-title').textContent = '待办事项';
            document.querySelector('.note-count').textContent = '0 条待办';
        }
    }

    // 切换侧边栏
    function toggleSidebar(open) {
        if (open) {
            sidebar.classList.add('open');
            sidebar.classList.remove('hidden');
            sidebarOverlay.classList.remove('hidden');
        } else {
            sidebar.classList.remove('open');
            setTimeout(() => {
                sidebar.classList.add('hidden');
                sidebarOverlay.classList.add('hidden');
            }, 300);
        }
    }

    // 保存到 localStorage
    function saveToLocalStorage() {
        localStorage.setItem('notes', JSON.stringify(notes));
    }

    // 格式化日期
    function formatDate(date) {
        const now = new Date();
        const diff = now - date;
        const oneDay = 24 * 60 * 60 * 1000;

        if (diff < oneDay && now.getDate() === date.getDate()) {
            return '今天';
        } else if (diff < 2 * oneDay && now.getDate() - date.getDate() === 1) {
            return '昨天';
        } else {
            const month = date.getMonth() + 1;
            const day = date.getDate();
            return `${month}月${day}日`;
        }
    }

    // HTML 转义
    function escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // ==================== 图片上传功能 ====================
    
    // 处理图片上传
    function handleImageUpload(e) {
        const files = Array.from(e.target.files);
        
        files.forEach(file => {
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    currentImages.push(event.target.result);
                    renderImagePreviews();
                };
                reader.readAsDataURL(file);
            }
        });
        
        // 清空input以便重复上传同一文件
        imageInput.value = '';
    }
    
    // 渲染图片预览
    function renderImagePreviews() {
        imagePreviewContainer.innerHTML = currentImages.map((img, index) => `
            <div class="image-preview-item">
                <img src="${img}" alt="预览图片">
                <button type="button" class="remove-image-btn" data-index="${index}">×</button>
            </div>
        `).join('');
        
        // 绑定删除按钮事件
        document.querySelectorAll('.remove-image-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const index = parseInt(btn.dataset.index);
                currentImages.splice(index, 1);
                renderImagePreviews();
            });
        });
    }
    
    // ==================== 编辑模式功能 ====================
    
    // 处理长按开始
    function handleLongPressStart(e, card) {
        if (isEditMode) return;
        
        longPressTimer = setTimeout(() => {
            card.classList.add('long-press-hint');
            enterEditMode();
            const id = parseInt(card.dataset.id);
            toggleNoteSelection(id, card);
        }, 500); // 500ms 长按触发
    }
    
    // 处理长按结束
    function handleLongPressEnd() {
        if (longPressTimer) {
            clearTimeout(longPressTimer);
            longPressTimer = null;
        }
    }
    
    // 进入编辑模式
    function enterEditMode() {
        isEditMode = true;
        editModeToolbar.classList.remove('hidden');
        addNoteBtn.style.display = 'none';
        renderNotes();
    }
    
    // 退出编辑模式
    function exitEditMode() {
        isEditMode = false;
        selectedNotes.clear();
        editModeToolbar.classList.add('hidden');
        addNoteBtn.style.display = 'flex';
        renderNotes();
    }
    
    // 切换笔记选中状态
    function toggleNoteSelection(id, card) {
        if (selectedNotes.has(id)) {
            selectedNotes.delete(id);
            card.classList.remove('selected');
        } else {
            selectedNotes.add(id);
            card.classList.add('selected');
        }
        updateSelectedCount();
    }
    
    // 更新选中数量
    function updateSelectedCount() {
        selectedCountEl.textContent = selectedNotes.size;
    }
    
    // 全选
    function selectAllNotes() {
        const allSelected = selectedNotes.size === notes.length;
        
        if (allSelected) {
            selectedNotes.clear();
        } else {
            notes.forEach(note => selectedNotes.add(note.id));
        }
        
        renderNotes();
        updateSelectedCount();
    }
    
    // 删除选中的笔记
    function deleteSelectedNotes() {
        if (selectedNotes.size === 0) return;
        
        if (confirm(`确定要删除 ${selectedNotes.size} 条备忘吗？`)) {
            notes = notes.filter(note => !selectedNotes.has(note.id));
            saveToLocalStorage();
            exitEditMode();
        }
    }
    
    // ==================== 触摸拖拽功能 ====================
    
    let touchStartY = 0;
    let touchStartX = 0;
    let isTouchDragging = false;
    let touchDraggedCard = null;
    let touchPlaceholder = null;
    
    function handleTouchStart(e, card) {
        const touch = e.touches[0];
        touchStartX = touch.clientX;
        touchStartY = touch.clientY;
        
        // 长按检测
        longPressTimer = setTimeout(() => {
            if (!isEditMode) {
                card.classList.add('long-press-hint');
                enterEditMode();
                const id = parseInt(card.dataset.id);
                toggleNoteSelection(id, card);
                // 触发震动反馈（如果支持）
                if (navigator.vibrate) {
                    navigator.vibrate(50);
                }
            } else {
                // 编辑模式下，长按开始拖拽
                startTouchDrag(e, card);
            }
        }, 500);
    }
    
    function handleTouchMove(e, card) {
        const touch = e.touches[0];
        const deltaX = Math.abs(touch.clientX - touchStartX);
        const deltaY = Math.abs(touch.clientY - touchStartY);
        
        // 如果移动距离超过阈值，取消长按
        if (!isTouchDragging && (deltaX > 10 || deltaY > 10)) {
            handleLongPressEnd();
        }
        
        // 处理拖拽移动
        if (isTouchDragging && touchDraggedCard) {
            e.preventDefault();
            moveTouchDrag(e);
        }
    }
    
    function handleTouchEnd(e, card) {
        handleLongPressEnd();
        
        if (isTouchDragging) {
            endTouchDrag(e);
            e.preventDefault();
            e.stopPropagation();
        } else if (isEditMode) {
            // 编辑模式下点击切换选中，阻止click事件触发
            e.preventDefault();
            e.stopPropagation();
            const id = parseInt(card.dataset.id);
            toggleNoteSelection(id, card);
        }
    }
    
    function startTouchDrag(e, card) {
        isTouchDragging = true;
        touchDraggedCard = card;
        card.classList.add('dragging');
        
        // 触发震动反馈
        if (navigator.vibrate) {
            navigator.vibrate(30);
        }
    }
    
    function moveTouchDrag(e) {
        if (!touchDraggedCard) return;
        
        const touch = e.touches[0];
        const elementBelow = document.elementFromPoint(touch.clientX, touch.clientY);
        const cardBelow = elementBelow?.closest('.note-card');
        
        // 移除所有 drag-over 样式
        document.querySelectorAll('.note-card.drag-over').forEach(c => {
            c.classList.remove('drag-over');
        });
        
        // 添加目标卡片的样式
        if (cardBelow && cardBelow !== touchDraggedCard) {
            cardBelow.classList.add('drag-over');
        }
    }
    
    function endTouchDrag(e) {
        if (!touchDraggedCard) return;
        
        // 找到放置目标
        const dragOverCard = document.querySelector('.note-card.drag-over');
        
        if (dragOverCard) {
            const draggedId = parseInt(touchDraggedCard.dataset.id);
            const targetId = parseInt(dragOverCard.dataset.id);
            
            const draggedIndex = notes.findIndex(n => n.id === draggedId);
            const targetIndex = notes.findIndex(n => n.id === targetId);
            
            if (draggedIndex !== -1 && targetIndex !== -1) {
                const [removed] = notes.splice(draggedIndex, 1);
                notes.splice(targetIndex, 0, removed);
                saveToLocalStorage();
                renderNotes();
            }
        }
        
        // 清理状态
        touchDraggedCard.classList.remove('dragging');
        document.querySelectorAll('.note-card.drag-over').forEach(c => {
            c.classList.remove('drag-over');
        });
        
        isTouchDragging = false;
        touchDraggedCard = null;
    }
    
    // ==================== 桌面端拖拽排序功能 ====================
    
    // 拖拽开始
    function handleDragStart(e, card) {
        if (!isEditMode) {
            e.preventDefault();
            return;
        }
        
        draggedNote = card;
        card.classList.add('dragging');
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/plain', card.dataset.id);
    }
    
    // 拖拽结束
    function handleDragEnd(e, card) {
        card.classList.remove('dragging');
        draggedNote = null;
        
        // 移除所有 drag-over 样式
        document.querySelectorAll('.note-card').forEach(c => {
            c.classList.remove('drag-over');
        });
    }
    
    // 拖拽经过
    function handleDragOver(e, card) {
        if (!isEditMode || card === draggedNote) return;
        
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
        card.classList.add('drag-over');
    }
    
    // 拖拽离开
    function handleDragLeave(e, card) {
        card.classList.remove('drag-over');
    }
    
    // 放置
    function handleDrop(e, card) {
        if (!isEditMode || !draggedNote || card === draggedNote) return;
        
        e.preventDefault();
        card.classList.remove('drag-over');
        
        const draggedId = parseInt(draggedNote.dataset.id);
        const targetId = parseInt(card.dataset.id);
        
        const draggedIndex = notes.findIndex(n => n.id === draggedId);
        const targetIndex = notes.findIndex(n => n.id === targetId);
        
        if (draggedIndex !== -1 && targetIndex !== -1) {
            // 移动元素
            const [removed] = notes.splice(draggedIndex, 1);
            notes.splice(targetIndex, 0, removed);
            
            saveToLocalStorage();
            renderNotes();
        }
    }
    
    // ==================== 下拉菜单功能 ====================
    
    const moreBtn = document.getElementById('moreBtn');
    const dropdownMenu = document.getElementById('dropdownMenu');
    const personalSpaceBtn = document.getElementById('personalSpaceBtn');
    const personalSpacePage = document.getElementById('personalSpacePage');
    const closePersonalSpace = document.getElementById('closePersonalSpace');
    const psCarouselWrapper = document.getElementById('psCarouselWrapper');
    const psCarousel = document.getElementById('psCarousel');
    const psIndicators = document.getElementById('psIndicators');
    const psCurrentIndex = document.getElementById('psCurrentIndex');
    const psTotalCount = document.getElementById('psTotalCount');
    const psAddNoteBtn = document.getElementById('psAddNoteBtn');
    
    let currentCardIndex = 0;
    let carouselStartX = 0;
    let carouselCurrentX = 0;
    let isDraggingCarousel = false;
    
    // 切换下拉菜单
    moreBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        dropdownMenu.classList.toggle('hidden');
    });
    
    // 点击其他地方关闭菜单
    document.addEventListener('click', (e) => {
        if (!dropdownMenu.contains(e.target) && e.target !== moreBtn) {
            dropdownMenu.classList.add('hidden');
        }
    });
    
    // 打开个人空间
    personalSpaceBtn.addEventListener('click', () => {
        dropdownMenu.classList.add('hidden');
        openPersonalSpace();
    });
    
    // 关闭个人空间
    closePersonalSpace.addEventListener('click', () => {
        closePersonalSpaceHandler();
    });
    
    // 个人空间内的添加按钮
    psAddNoteBtn.addEventListener('click', () => {
        closePersonalSpaceHandler();
        setTimeout(() => openModal(), 300);
    });
    
    function openPersonalSpace() {
        personalSpacePage.classList.remove('hidden');
        currentCardIndex = 0;
        renderCarousel();
        bindCarouselEvents();
    }
    
    function closePersonalSpaceHandler() {
        personalSpacePage.classList.add('hidden');
    }
    
    // 渲染轮播卡片
    function renderCarousel() {
        psTotalCount.textContent = notes.length;
        
        if (notes.length === 0) {
            psCarousel.innerHTML = '';
            psIndicators.innerHTML = '';
            psCurrentIndex.textContent = '0';
            return;
        }
        
        // 渲染所有卡片
        psCarousel.innerHTML = notes.map((note, index) => createPsCard(note, index)).join('');
        
        // 渲染指示器
        psIndicators.innerHTML = notes.map((_, index) => 
            `<div class="ps-indicator ${index === currentCardIndex ? 'active' : ''}"></div>`
        ).join('');
        
        updateCarouselPosition(false);
        updateCardStates();
    }
    
    // 创建个人空间卡片HTML
    function createPsCard(note, index) {
        const starHtml = note.starred ? '<span class="ps-card-star">★</span>' : '';
        
        let imagesHtml = '';
        if (note.images && note.images.length > 0) {
            imagesHtml = `
                <div class="ps-card-images">
                    ${note.images.map(img => `<img src="${img}" alt="">`).join('')}
                </div>
            `;
        } else if (note.thumbnail) {
            imagesHtml = `
                <div class="ps-card-images">
                    <img src="${note.thumbnail}" alt="">
                </div>
            `;
        }
        
        return `
            <div class="ps-card" data-id="${note.id}" data-index="${index}">
                <div class="ps-card-header">
                    <span class="ps-card-date">${note.date}</span>
                    ${starHtml}
                </div>
                <h3 class="ps-card-title">${escapeHtml(note.title) || '无标题'}</h3>
                <div class="ps-card-content">${escapeHtml(note.content) || '无内容'}</div>
                ${imagesHtml}
            </div>
        `;
    }
    
    // 更新轮播位置
    function updateCarouselPosition(animate = true) {
        const cardWidth = 300;
        const gap = 16;
        const offset = currentCardIndex * (cardWidth + gap);
        
        psCarousel.style.transition = animate ? 'transform 0.4s cubic-bezier(0.25, 0.1, 0.25, 1)' : 'none';
        psCarousel.style.transform = `translateX(-${offset}px)`;
    }
    
    // 更新卡片状态
    function updateCardStates() {
        updateCardStatesVisual(currentCardIndex);
    }
    
    // 根据指定索引更新卡片视觉状态
    function updateCardStatesVisual(activeIndex) {
        document.querySelectorAll('.ps-card').forEach((card, index) => {
            card.classList.remove('active', 'prev', 'next');
            
            if (index === activeIndex) {
                card.classList.add('active');
            } else if (index === activeIndex - 1) {
                card.classList.add('prev');
            } else if (index === activeIndex + 1) {
                card.classList.add('next');
            }
        });
        
        // 更新指示器
        document.querySelectorAll('.ps-indicator').forEach((indicator, index) => {
            indicator.classList.toggle('active', index === activeIndex);
        });
        
        // 更新索引显示
        psCurrentIndex.textContent = activeIndex + 1;
    }
    
    // 绑定轮播事件 - 在整个wrapper区域
    function bindCarouselEvents() {
        const wrapper = psCarouselWrapper;
        const carousel = psCarousel;
        
        const onStart = (e) => {
            // 如果点击的是FAB按钮，不处理
            if (e.target.closest('.ps-fab')) return;
            
            isDraggingCarousel = true;
            carousel.classList.add('dragging');
            const point = e.touches ? e.touches[0] : e;
            carouselStartX = point.clientX;
            carouselCurrentX = 0;
        };
        
        const onMove = (e) => {
            if (!isDraggingCarousel) return;
            
            const point = e.touches ? e.touches[0] : e;
            carouselCurrentX = point.clientX - carouselStartX;
            
            const cardWidth = 300;
            const gap = 16;
            const baseOffset = currentCardIndex * (cardWidth + gap);
            
            carousel.style.transition = 'none';
            carousel.style.transform = `translateX(${-baseOffset + carouselCurrentX}px)`;
            
            // 实时更新卡片状态 - 根据滑动距离计算当前应该高亮的卡片
            // 当滑动超过卡片宽度一半时切换active状态
            const halfCard = (cardWidth + gap) / 2;
            let visualIndex = currentCardIndex;
            
            if (carouselCurrentX < -halfCard) {
                // 向左滑超过一半，下一张active
                visualIndex = Math.min(notes.length - 1, currentCardIndex + Math.ceil(-carouselCurrentX / (cardWidth + gap)));
            } else if (carouselCurrentX > halfCard) {
                // 向右滑超过一半，上一张active
                visualIndex = Math.max(0, currentCardIndex - Math.ceil(carouselCurrentX / (cardWidth + gap)));
            }
            
            updateCardStatesVisual(visualIndex);
        };
        
        const onEnd = (e) => {
            if (!isDraggingCarousel) return;
            isDraggingCarousel = false;
            carousel.classList.remove('dragging');
            
            const threshold = 60;
            
            if (carouselCurrentX < -threshold && currentCardIndex < notes.length - 1) {
                // 向左滑 - 下一张
                currentCardIndex++;
            } else if (carouselCurrentX > threshold && currentCardIndex > 0) {
                // 向右滑 - 上一张
                currentCardIndex--;
            }
            
            updateCarouselPosition(true);
            updateCardStates();
            
            // 检测是否为点击（非拖拽）
            if (Math.abs(carouselCurrentX) < 10) {
                const card = e.target.closest('.ps-card');
                if (card && card.classList.contains('active')) {
                    const noteId = parseInt(card.dataset.id);
                    closePersonalSpaceHandler();
                    setTimeout(() => openModal(noteId), 300);
                }
            }
            
            carouselCurrentX = 0;
        };
        
        // 绑定到wrapper而不是carousel
        wrapper.onmousedown = onStart;
        wrapper.ontouchstart = onStart;
        
        wrapper.onmousemove = onMove;
        wrapper.ontouchmove = onMove;
        
        wrapper.onmouseup = onEnd;
        wrapper.ontouchend = onEnd;
        
        // 防止拖拽时离开wrapper区域
        wrapper.onmouseleave = () => {
            if (isDraggingCarousel) {
                isDraggingCarousel = false;
                carousel.classList.remove('dragging');
                updateCarouselPosition(true);
                carouselCurrentX = 0;
            }
        };
    }
});
