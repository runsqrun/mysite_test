// 标签页切换功能
document.addEventListener('DOMContentLoaded', function() {
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const targetId = this.getAttribute('data-tab');
            
            // 移除所有活动状态
            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(tc => tc.classList.remove('active'));
            
            // 添加当前活动状态
            this.classList.add('active');
            document.getElementById(targetId).classList.add('active');
        });
    });
    
    // 评分条动画
    const bars = document.querySelectorAll('.bar, .sentiment-bar');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.width = entry.target.style.width;
            }
        });
    }, { threshold: 0.5 });
    
    bars.forEach(bar => {
        const width = bar.style.width;
        bar.style.width = '0';
        observer.observe(bar);
        setTimeout(() => {
            bar.style.width = width;
        }, 300);
    });
    
    // 想看/看过按钮交互
    const btnPrimary = document.querySelector('.btn-primary');
    const btnSecondary = document.querySelector('.btn-secondary');
    
    if (btnPrimary) {
        btnPrimary.addEventListener('click', function() {
            if (this.classList.contains('added')) {
                this.innerHTML = '<span class="btn-icon">➕</span> 想看';
                this.classList.remove('added');
            } else {
                this.innerHTML = '<span class="btn-icon">✓</span> 已添加';
                this.classList.add('added');
                showToast('已添加到想看列表');
            }
        });
    }
    
    if (btnSecondary) {
        btnSecondary.addEventListener('click', function() {
            showRatingModal();
        });
    }
    
    // 关键词点击效果
    const keywords = document.querySelectorAll('.keyword');
    keywords.forEach(keyword => {
        keyword.addEventListener('click', function() {
            const text = this.textContent;
            highlightReviewsWithKeyword(text);
        });
    });
});

// 显示提示消息
function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 30px;
        left: 50%;
        transform: translateX(-50%);
        background: #00dc7d;
        color: #000;
        padding: 12px 24px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 500;
        z-index: 10000;
        animation: fadeInUp 0.3s ease;
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 2000);
}

// 显示评分弹窗
function showRatingModal() {
    const modal = document.createElement('div');
    modal.className = 'rating-modal';
    modal.innerHTML = `
        <div class="modal-overlay"></div>
        <div class="modal-content">
            <h3>为这部电影评分</h3>
            <div class="star-rating">
                <span class="star" data-rating="1">☆</span>
                <span class="star" data-rating="2">☆</span>
                <span class="star" data-rating="3">☆</span>
                <span class="star" data-rating="4">☆</span>
                <span class="star" data-rating="5">☆</span>
            </div>
            <p class="rating-text">点击星星评分</p>
            <div class="modal-buttons">
                <button class="modal-cancel">取消</button>
                <button class="modal-confirm">确认</button>
            </div>
        </div>
    `;
    
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
    `;
    
    const style = document.createElement('style');
    style.textContent = `
        .modal-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
        }
        .modal-content {
            position: relative;
            background: #2a2a2a;
            padding: 32px;
            border-radius: 16px;
            text-align: center;
            min-width: 320px;
        }
        .modal-content h3 {
            margin-bottom: 24px;
            font-size: 18px;
        }
        .star-rating {
            font-size: 40px;
            margin-bottom: 16px;
        }
        .star {
            cursor: pointer;
            color: #555;
            transition: all 0.2s;
        }
        .star:hover,
        .star.active {
            color: #ffd93d;
        }
        .rating-text {
            color: #888;
            font-size: 14px;
            margin-bottom: 24px;
        }
        .modal-buttons {
            display: flex;
            gap: 12px;
            justify-content: center;
        }
        .modal-cancel,
        .modal-confirm {
            padding: 10px 24px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .modal-cancel {
            background: #3a3a3a;
            color: #fff;
        }
        .modal-confirm {
            background: #00dc7d;
            color: #000;
        }
        .modal-cancel:hover {
            background: #4a4a4a;
        }
        .modal-confirm:hover {
            background: #00ff8f;
        }
    `;
    
    document.head.appendChild(style);
    document.body.appendChild(modal);
    
    let selectedRating = 0;
    const stars = modal.querySelectorAll('.star');
    const ratingText = modal.querySelector('.rating-text');
    const ratingTexts = ['', '很差', '较差', '还行', '推荐', '力荐'];
    
    stars.forEach(star => {
        star.addEventListener('mouseover', function() {
            const rating = parseInt(this.dataset.rating);
            updateStars(rating);
            ratingText.textContent = ratingTexts[rating];
        });
        
        star.addEventListener('mouseout', function() {
            updateStars(selectedRating);
            ratingText.textContent = selectedRating ? ratingTexts[selectedRating] : '点击星星评分';
        });
        
        star.addEventListener('click', function() {
            selectedRating = parseInt(this.dataset.rating);
            updateStars(selectedRating);
            ratingText.textContent = ratingTexts[selectedRating];
        });
    });
    
    function updateStars(rating) {
        stars.forEach((star, index) => {
            if (index < rating) {
                star.textContent = '★';
                star.classList.add('active');
            } else {
                star.textContent = '☆';
                star.classList.remove('active');
            }
        });
    }
    
    modal.querySelector('.modal-overlay').addEventListener('click', () => modal.remove());
    modal.querySelector('.modal-cancel').addEventListener('click', () => modal.remove());
    modal.querySelector('.modal-confirm').addEventListener('click', () => {
        if (selectedRating) {
            showToast(`已评分：${selectedRating}星 (${ratingTexts[selectedRating]})`);
            const btnSecondary = document.querySelector('.btn-secondary');
            btnSecondary.innerHTML = `<span class="btn-icon">★</span> ${selectedRating}星`;
            btnSecondary.style.borderColor = '#00dc7d';
            btnSecondary.style.color = '#00dc7d';
        }
        modal.remove();
    });
}

// 高亮包含关键词的评论
function highlightReviewsWithKeyword(keyword) {
    const reviewContents = document.querySelectorAll('.review-content');
    let found = false;
    
    reviewContents.forEach(content => {
        content.innerHTML = content.textContent; // 清除之前的高亮
        
        if (content.textContent.includes(keyword)) {
            const regex = new RegExp(`(${keyword})`, 'g');
            content.innerHTML = content.textContent.replace(regex, '<mark style="background: #00dc7d; color: #000; padding: 0 2px; border-radius: 2px;">$1</mark>');
            found = true;
        }
    });
    
    if (found) {
        showToast(`已高亮包含"${keyword}"的评论`);
    } else {
        showToast(`未找到包含"${keyword}"的评论`);
    }
}

// 添加动画样式
const animationStyle = document.createElement('style');
animationStyle.textContent = `
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translate(-50%, 20px);
        }
        to {
            opacity: 1;
            transform: translate(-50%, 0);
        }
    }
    
    @keyframes fadeOut {
        from {
            opacity: 1;
        }
        to {
            opacity: 0;
        }
    }
`;
document.head.appendChild(animationStyle);

// 页面滚动效果
let lastScrollTop = 0;
const navbar = document.querySelector('.navbar');

window.addEventListener('scroll', function() {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    
    if (scrollTop > lastScrollTop && scrollTop > 100) {
        navbar.style.transform = 'translateY(-100%)';
    } else {
        navbar.style.transform = 'translateY(0)';
    }
    
    lastScrollTop = scrollTop;
});

// 添加导航栏过渡效果
navbar.style.transition = 'transform 0.3s ease';

// 查看更多按钮
const viewMoreBtn = document.querySelector('.view-more-btn');
if (viewMoreBtn) {
    viewMoreBtn.addEventListener('click', function() {
        showToast('功能开发中，敬请期待...');
    });
}

console.log('🎬 电影评论页面加载完成');
console.log('📊 数据来源: 豆瓣电影爬虫');
console.log('📅 爬取时间: 2026-01-21');
