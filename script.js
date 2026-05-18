/* =========================================================
   渊学通杭州校区 · 毕业典礼邀请函 交互脚本
   - 背景音乐自动播放 (用户触屏后)
   - 滚动入场动画
   - RSVP 交互
   ========================================================= */

(function () {
    'use strict';

    // =====================================================
    // 1. 背景音乐控制
    //    - 进入页面立即尝试自动播放
    //    - 被浏览器拦截时，监听首次用户交互再播放
    //    - 左上角按钮可手动暂停/恢复
    // =====================================================
    const bgMusic  = document.getElementById('bgMusic');
    const musicBtn = document.getElementById('musicBtn');

    let isPlaying = false;
    let userInteracted = false;

    function setBtnState(on) {
        if (!musicBtn) return;
        if (on) musicBtn.classList.add('on');
        else    musicBtn.classList.remove('on');
    }

    function tryPlay() {
        if (!bgMusic) return;
        bgMusic.volume = 0.4;
        const p = bgMusic.play();
        if (p !== undefined) {
            p.then(() => {
                isPlaying = true;
                setBtnState(true);
            }).catch(() => {
                // 自动播放被拦截，等用户首次交互
                isPlaying = false;
                setBtnState(false);
            });
        }
    }

    function pauseMusic() {
        if (!bgMusic) return;
        bgMusic.pause();
        isPlaying = false;
        setBtnState(false);
    }

    function toggleMusic() {
        if (isPlaying) pauseMusic();
        else tryPlay();
    }

    // 按钮：手动开关
    if (musicBtn) {
        musicBtn.addEventListener('click', toggleMusic);
    }

    // 进入页面立即尝试播放
    if (bgMusic) {
        tryPlay();
    }

    // 浏览器拦截了？监听首次用户交互（点击/触摸/滚动/键盘）后自动播放
    function onFirstInteract() {
        if (userInteracted) return;
        userInteracted = true;
        if (bgMusic && bgMusic.paused) {
            tryPlay();
        }
        ['click', 'touchstart', 'keydown', 'scroll'].forEach(ev =>
            window.removeEventListener(ev, onFirstInteract, true)
        );
    }
    ['click', 'touchstart', 'keydown', 'scroll'].forEach(ev =>
        window.addEventListener(ev, onFirstInteract, { capture: true, passive: true })
    );

    // =====================================================
    // 2. 滚动进入动画 (IntersectionObserver)
    // =====================================================
    const revealEls = document.querySelectorAll('.reveal');

    if ('IntersectionObserver' in window) {
        const io = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('show');
                    } else {
                        entry.target.classList.remove('show');
                    }
                });
            },
            { threshold: 0.25 }
        );

        revealEls.forEach((el) => io.observe(el));
    } else {
        // 降级：直接显示
        revealEls.forEach((el) => el.classList.add('show'));
    }

    // =====================================================
    // 3. RSVP 弹层
    // =====================================================
    const rsvpBtn    = document.getElementById('rsvpBtn');
    const modal      = document.getElementById('rsvpModal');
    const modalClose = document.getElementById('modalClose');

    if (rsvpBtn && modal) {
        rsvpBtn.addEventListener('click', () => modal.classList.add('show'));
    }
    if (modalClose && modal) {
        modalClose.addEventListener('click', () => modal.classList.remove('show'));
    }
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.classList.remove('show');
        });
    }

    // =====================================================
    // 4. 额外：为樱花添加随机化延迟（增强自然感）
    // =====================================================
    const sakuras = document.querySelectorAll('.sakura');
    sakuras.forEach((s) => {
        const randomDelay = (Math.random() * 5).toFixed(2);
        const randomDur   = (7 + Math.random() * 6).toFixed(2);
        s.style.animationDelay = randomDelay + 's, ' + randomDelay + 's';
        s.style.animationDuration = randomDur + 's, ' + (3 + Math.random() * 2).toFixed(2) + 's';
    });

    // =====================================================
    // 5. 封面图片预加载（每屏独立背景，无轮播）
    // =====================================================
    document.querySelectorAll('.page-bg').forEach((bg) => {
        const url = bg.style.backgroundImage.replace(/^url\(['"]?/, '').replace(/['"]?\)$/, '');
        if (url) {
            const img = new Image();
            img.src = url;
        }
    });

})();
