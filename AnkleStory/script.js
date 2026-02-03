// Ankle Story - 100 Days Progress Tracker

document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const progressFill = document.querySelector('.progress-fill');
    const progressDot = document.querySelector('.progress-dot');
    const currentDayEl = document.getElementById('current-day');
    const stepsCountEl = document.getElementById('steps-count');
    const milesCountEl = document.getElementById('miles-count');
    const dayIndicator = document.querySelector('.day-indicator');
    const daySections = document.querySelectorAll('.day-section');

    // Stats data for each day milestone
    const dayStats = {
        0: { steps: 0, miles: 0 },
        1: { steps: 50, miles: 0 },
        2: { steps: 120, miles: 0.05 },
        7: { steps: 500, miles: 0.2 },
        14: { steps: 1200, miles: 0.5 },
        30: { steps: 3500, miles: 1.5 },
        45: { steps: 8000, miles: 3.5 },
        60: { steps: 15000, miles: 6.5 },
        75: { steps: 28000, miles: 12 },
        100: { steps: 42675, miles: 19 }
    };

    // Get all day milestones
    const dayMilestones = Array.from(daySections).map(section => 
        parseInt(section.dataset.day)
    ).sort((a, b) => a - b);

    // Interpolate stats between milestones
    function getStatsForDay(day) {
        const milestones = Object.keys(dayStats).map(Number).sort((a, b) => a - b);
        
        // Find surrounding milestones
        let lowerMilestone = 0;
        let upperMilestone = 100;
        
        for (let i = 0; i < milestones.length; i++) {
            if (milestones[i] <= day) {
                lowerMilestone = milestones[i];
            }
            if (milestones[i] >= day) {
                upperMilestone = milestones[i];
                break;
            }
        }
        
        if (lowerMilestone === upperMilestone) {
            return dayStats[lowerMilestone];
        }
        
        // Interpolate
        const progress = (day - lowerMilestone) / (upperMilestone - lowerMilestone);
        const lowerStats = dayStats[lowerMilestone];
        const upperStats = dayStats[upperMilestone];
        
        return {
            steps: Math.round(lowerStats.steps + (upperStats.steps - lowerStats.steps) * progress),
            miles: Math.round((lowerStats.miles + (upperStats.miles - lowerStats.miles) * progress) * 10) / 10
        };
    }

    // Format number with commas
    function formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }

    // Calculate scroll progress
    function updateProgress() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
        const scrollProgress = Math.min(Math.max(scrollTop / scrollHeight, 0), 1);
        
        // Update progress bar
        const progressPercent = scrollProgress * 100;
        progressFill.style.width = `${progressPercent}%`;
        progressDot.style.left = `${progressPercent}%`;
        
        // Calculate current day (0-100)
        const currentDay = Math.round(scrollProgress * 100);
        currentDayEl.textContent = currentDay;
        
        // Update stats
        const stats = getStatsForDay(currentDay);
        stepsCountEl.textContent = formatNumber(stats.steps);
        milesCountEl.textContent = stats.miles;
        
        // Show/hide day indicator based on scroll
        if (scrollTop > 100) {
            dayIndicator.classList.add('visible');
        } else {
            dayIndicator.classList.remove('visible');
        }
        
        // Highlight current section
        highlightCurrentSection(scrollTop);
    }

    // Highlight the section currently in view
    function highlightCurrentSection(scrollTop) {
        const windowHeight = window.innerHeight;
        
        daySections.forEach(section => {
            const rect = section.getBoundingClientRect();
            const sectionTop = rect.top;
            const sectionBottom = rect.bottom;
            
            // Check if section is in viewport
            if (sectionTop < windowHeight * 0.5 && sectionBottom > windowHeight * 0.5) {
                section.classList.add('active');
            } else {
                section.classList.remove('active');
            }
        });
    }

    // Throttle scroll events for performance
    let ticking = false;
    function onScroll() {
        if (!ticking) {
            window.requestAnimationFrame(() => {
                updateProgress();
                ticking = false;
            });
            ticking = true;
        }
    }

    // Event listeners
    window.addEventListener('scroll', onScroll);
    window.addEventListener('resize', updateProgress);

    // Initial update
    updateProgress();

    // Smooth scroll to section when clicking on progress bar
    document.querySelector('.progress-container').addEventListener('click', (e) => {
        const rect = e.currentTarget.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const clickPercent = clickX / rect.width;
        const targetScroll = clickPercent * (document.documentElement.scrollHeight - window.innerHeight);
        
        window.scrollTo({
            top: targetScroll,
            behavior: 'smooth'
        });
    });

    // Optional: Add intersection observer for lazy loading images
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                if (img.dataset.src) {
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    observer.unobserve(img);
                }
            }
        });
    }, {
        rootMargin: '50px 0px',
        threshold: 0.01
    });

    // Observe all images with data-src attribute
    document.querySelectorAll('img[data-src]').forEach(img => {
        imageObserver.observe(img);
    });

    // Text button functionality (toggle text visibility)
    const textBtn = document.querySelector('.text-btn');
    let textVisible = true;
    
    textBtn.addEventListener('click', () => {
        textVisible = !textVisible;
        document.querySelectorAll('.text-block').forEach(block => {
            block.style.opacity = textVisible ? '1' : '0.3';
        });
        textBtn.classList.toggle('active', !textVisible);
    });

    console.log('Ankle Story loaded successfully!');
});
