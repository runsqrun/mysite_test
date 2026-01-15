const contentContainer = document.querySelector('.content-container');
const sections = document.querySelectorAll('.scroll-section');
const mainImage = document.getElementById('mainImage');
const highlightBox = document.getElementById('highlightBox');
const imageContainer = document.querySelector('.image-container');
const TOTAL_ROWS = 21;

let imageHeight = 0;

// 计算图片实际显示的高度
function updateImageHeight() {
    imageHeight = mainImage.getBoundingClientRect().height;
    console.log('图片高度:', imageHeight);
}

// 更新高亮框位置
function updateHighlightPosition(activeIndex) {
    if (imageHeight === 0 || activeIndex === -1) return;
    
    // 确保索引在0-20范围内
    const rowIndex = Math.min(Math.max(activeIndex, 0), TOTAL_ROWS - 1);
    
    // 计算每行高度和该行的Y位置
    const rowHeight = imageHeight / TOTAL_ROWS;
    
    // 计算容器内图片的垂直偏移（因为图片垂直居中）
    const containerHeight = imageContainer.clientHeight;
    const verticalOffset = (containerHeight - imageHeight) / 2;
    
    // 计算高亮框位置
    const highlightTop = verticalOffset + (rowIndex * rowHeight);
    const highlightHeight = rowHeight;
    
    // 获取图片的水平位置和宽度
    const imageRect = mainImage.getBoundingClientRect();
    const imageLeft = imageRect.left;
    const imageWidth = imageRect.width;
    
    highlightBox.style.top = highlightTop + 'px';
    highlightBox.style.height = highlightHeight + 'px';
    highlightBox.style.left = (imageLeft + imageWidth / 2) + 'px';
    highlightBox.style.width = (imageWidth * 0.95) + 'px';
    highlightBox.classList.add('active');
    
    console.log('高亮行号:', rowIndex, '位置:', highlightTop, '高度:', highlightHeight);
}

// 处理滚动
function handleScroll() {
    // 获取屏幕中心Y坐标（相对于视口）
    const screenCenterY = window.innerHeight / 2;
    
    let activeIndex = -1;
    let minDistance = Infinity;
    
    // 找到最接近屏幕中心的section
    sections.forEach((section, index) => {
        const rect = section.getBoundingClientRect();
        // section的中心点相对于视口的Y坐标
        const sectionCenterY = rect.top + rect.height / 2;
        
        // 计算到屏幕中心的距离
        const distance = Math.abs(sectionCenterY - screenCenterY);
        if (distance < minDistance) {
            minDistance = distance;
            activeIndex = index;
        }
    });
    
    // 更新所有section的active状态
    if (activeIndex !== -1) {
        sections.forEach((s, i) => {
            if (i === activeIndex) {
                s.classList.add('active');
            } else {
                s.classList.remove('active');
            }
        });
        
        console.log('当前section索引:', activeIndex);
        updateHighlightPosition(activeIndex);
    }
}

// 监听右侧内容滚动
contentContainer.addEventListener('scroll', handleScroll);

// 监听窗口resize
window.addEventListener('resize', () => {
    updateImageHeight();
    handleScroll();
});

// 页面加载完成后初始化
window.addEventListener('load', () => {
    updateImageHeight();
    // 滚动到顶部，确保从第一行开始
    contentContainer.scrollTop = 0;
    // 初始化高亮为第一行
    setTimeout(() => {
        handleScroll();
    }, 100);
});

// 如果图片已缓存，立即更新
if (mainImage.complete) {
    updateImageHeight();
}
