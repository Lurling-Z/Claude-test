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
    // =====================================================
    const bgMusic      = document.getElementById('bgMusic');
    const musicBtn     = document.getElementById('musicBtn');
    const musicOverlay = document.getElementById('musicOverlay');
    const playIcon     = document.getElementById('playIcon');

    let isPlaying = false;

    function playMusic() {
        if (!bgMusic) return;
        bgMusic.volume = 0.4;
        const promise = bgMusic.play();
        if (promise !== undefined) {
            promise.then(() => {
                isPlaying = true;
                if (musicBtn) musicBtn.classList.add('on');
            }).catch(() => {
                // 浏览器阻止了自动播放，保持overlay可见
                if (musicOverlay) musicOverlay.classList.remove('hidden');
            });
        }
    }

    function pauseMusic() {
        if (!bgMusic) return;
        bgMusic.pause();
        isPlaying = false;
        if (musicBtn) musicBtn.classList.remove('on');
    }

    function toggleMusic() {
        if (isPlaying) {
            pauseMusic();
        } else {
            playMusic();
        }
    }

    // 音乐引导弹层：点击播放按钮
    if (playIcon && musicOverlay) {
        playIcon.addEventListener('click', function () {
            musicOverlay.classList.add('hidden');
            playMusic();
        });
        // 点击弹层任意位置也可关闭并播放
        musicOverlay.addEventListener('click', function (e) {
            if (e.target === musicOverlay) {
                musicOverlay.classList.add('hidden');
                playMusic();
            }
        });
    }

    // 音乐按钮切换
    if (musicBtn) {
        musicBtn.addEventListener('click', toggleMusic);
    }

    // 尝试自动播放（部分浏览器允许静音自动播放后取消静音）
    // 大多移动浏览器需要用户交互，所以展示overlay
    if (bgMusic) {
        // 先尝试播放
        bgMusic.volume = 0.4;
        const autoPlayPromise = bgMusic.play();
        if (autoPlayPromise !== undefined) {
            autoPlayPromise.then(() => {
                // 自动播放成功，隐藏overlay
                isPlaying = true;
                if (musicBtn) musicBtn.classList.add('on');
                if (musicOverlay) musicOverlay.classList.add('hidden');
            }).catch(() => {
                // 自动播放被阻止，显示overlay让用户点击
                if (musicOverlay) musicOverlay.classList.remove('hidden');
            });
        }
    }

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

})();
