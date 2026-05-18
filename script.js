/* =========================================================
   渊学通杭州校区 · 毕业典礼邀请函 交互脚本
   - 背景音乐：点击弹层后播放（解决浏览器自动播放拦截）
   - 滚动入场动画
   - RSVP 交互
   ========================================================= */

(function () {
    'use strict';

    // =====================================================
    // 1. 背景音乐控制 — 通过用户主动点击弹层启动
    // =====================================================
    const bgMusic      = document.getElementById('bgMusic');
    const musicBtn     = document.getElementById('musicBtn');
    const musicOverlay = document.getElementById('musicOverlay');
    const playIcon     = document.getElementById('playIcon');

    let isPlaying = false;

    function setBtnState(on) {
        if (!musicBtn) return;
        if (on) musicBtn.classList.add('on');
        else    musicBtn.classList.remove('on');
    }

    function playMusic() {
        if (!bgMusic) return;
        bgMusic.volume = 0.4;
        // 用户点击后再加载音频
        try { bgMusic.load(); } catch (e) {}
        const p = bgMusic.play();
        if (p !== undefined) {
            p.then(() => {
                isPlaying = true;
                setBtnState(true);
            }).catch(() => {
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
        else playMusic();
    }

    // 音乐启动弹层：点击后播放音乐并关闭弹层
    function dismissOverlay() {
        if (musicOverlay) {
            musicOverlay.classList.add('hidden');
        }
        playMusic();
        // 用户点击后再触发图片预加载，加速后续滚动浏览体验
        preloadAllImages();
    }

    if (playIcon) {
        playIcon.addEventListener('click', dismissOverlay);
    }
    if (musicOverlay) {
        musicOverlay.addEventListener('click', dismissOverlay);
    }

    // 左上角按钮：手动开关
    if (musicBtn) {
        musicBtn.addEventListener('click', toggleMusic);
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

    // =====================================================
    // 5. 封面图片预加载（用户点击开屏后才预加载，加速首屏）
    // =====================================================
    function preloadAllImages() {
        document.querySelectorAll('.page-bg').forEach((bg) => {
            const url = bg.style.backgroundImage.replace(/^url\(['"]?/, '').replace(/['"]?\)$/, '');
            if (url) {
                const img = new Image();
                img.src = url;
            }
        });
    }

})();
