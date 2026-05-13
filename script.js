/* =========================================================
   渊学通杭州校区 · 毕业典礼邀请函 交互脚本
   ========================================================= */

(function () {
    // ---------- 1. 滚动进入动画 ----------
    const revealEls = document.querySelectorAll('.reveal');

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
        { threshold: 0.3 }
    );

    revealEls.forEach((el) => io.observe(el));

    // ---------- 2. 音乐按钮（占位：不加载实际音频，仅切换视觉状态） ----------
    const musicBtn = document.getElementById('musicBtn');
    if (musicBtn) {
        musicBtn.classList.add('on'); // 默认视觉"播放"态
        musicBtn.addEventListener('click', () => {
            musicBtn.classList.toggle('on');
        });
    }

    // ---------- 3. RSVP ----------
    const rsvpBtn   = document.getElementById('rsvpBtn');
    const modal     = document.getElementById('rsvpModal');
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
})();
