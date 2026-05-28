/* ================================================================
   小红书笔记详情页 复刻 - 交互脚本
   - 12 图轮播（点击箭头 / 圆点 / 键盘左右）
   - 图片加载失败时回退到带序号的占位 SVG
   - 评论 like / 关注按钮等基础交互
   ================================================================ */

(function () {
  const slides = Array.from(document.querySelectorAll('.slide'));
  const dotsBox = document.getElementById('dots');
  const fractionEl = document.getElementById('cur');
  const prevBtn = document.getElementById('prev');
  const nextBtn = document.getElementById('next');
  const total = slides.length;
  let cur = 0;

  // ========== 1. 图片回退占位（CDN 时效令牌可能失效） ==========
  function makePlaceholder(num) {
    const colors = ['#ffe5e9', '#ffe9d6', '#fff7d8', '#e6f7e9', '#dff1ff',
                    '#e9defc', '#fce0f4', '#ffd6dd', '#f7e6c4', '#d9f0e6',
                    '#e2d8ff', '#ffd9c2'];
    const bg = colors[(num - 1) % colors.length];
    const svg = `<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 600 800'>
      <rect width='600' height='800' fill='${bg}'/>
      <text x='50%' y='46%' font-family='PingFang SC,sans-serif' font-size='180'
            fill='rgba(255,36,66,0.55)' text-anchor='middle' font-weight='800'>${num}</text>
      <text x='50%' y='60%' font-family='PingFang SC,sans-serif' font-size='28'
            fill='rgba(0,0,0,0.5)' text-anchor='middle'>第 ${num} / 12 张</text>
      <text x='50%' y='66%' font-family='PingFang SC,sans-serif' font-size='18'
            fill='rgba(0,0,0,0.35)' text-anchor='middle'>原图受 CDN 时效令牌限制</text>
    </svg>`;
    return 'data:image/svg+xml;utf8,' + encodeURIComponent(svg);
  }

  slides.forEach((slide, i) => {
    const img = slide.querySelector('img');
    if (!img) return;
    img.addEventListener('error', () => {
      img.src = makePlaceholder(i + 1);
      img.dataset.fallbackUsed = '1';
    }, { once: true });
    // 兜底：如果是 lazy/慢图，1.6s 仍未加载就也走占位（避免长时间空白）
    setTimeout(() => {
      if (!img.complete || img.naturalWidth === 0) {
        if (!img.dataset.fallbackUsed) {
          img.src = makePlaceholder(i + 1);
          img.dataset.fallbackUsed = '1';
        }
      }
    }, 1600);
  });

  // ========== 2. 渲染圆点 ==========
  for (let i = 0; i < total; i++) {
    const d = document.createElement('span');
    d.className = 'dot' + (i === 0 ? ' is-active' : '');
    d.dataset.idx = i;
    d.addEventListener('click', () => go(i));
    dotsBox.appendChild(d);
  }
  const dots = Array.from(dotsBox.querySelectorAll('.dot'));

  // ========== 3. 翻页 ==========
  function go(i) {
    if (i < 0) i = 0;
    if (i > total - 1) i = total - 1;
    if (i === cur) return;
    slides[cur].classList.remove('is-active');
    dots[cur].classList.remove('is-active');
    cur = i;
    slides[cur].classList.add('is-active');
    dots[cur].classList.add('is-active');
    fractionEl.textContent = cur + 1;
    updateArrows();
  }

  function updateArrows() {
    prevBtn.disabled = cur === 0;
    nextBtn.disabled = cur === total - 1;
  }

  prevBtn.addEventListener('click', () => go(cur - 1));
  nextBtn.addEventListener('click', () => go(cur + 1));

  // 键盘左右
  document.addEventListener('keydown', (e) => {
    if (e.target && /^(INPUT|TEXTAREA)$/.test(e.target.tagName)) return;
    if (e.key === 'ArrowLeft') go(cur - 1);
    else if (e.key === 'ArrowRight') go(cur + 1);
  });

  // 触屏左右滑（移动端）
  let touchStartX = 0;
  const mediaEl = document.querySelector('.media');
  if (mediaEl) {
    mediaEl.addEventListener('touchstart', (e) => {
      touchStartX = e.changedTouches[0].clientX;
    }, { passive: true });
    mediaEl.addEventListener('touchend', (e) => {
      const dx = e.changedTouches[0].clientX - touchStartX;
      if (Math.abs(dx) < 40) return;
      if (dx > 0) go(cur - 1);
      else go(cur + 1);
    });
  }

  updateArrows();

  // ========== 4. 评论：展开子回复 ==========
  document.querySelectorAll('.show-more').forEach((el) => {
    el.addEventListener('click', () => {
      el.textContent = '— 已展开（演示）—';
      el.style.color = '#bbb';
      el.style.cursor = 'default';
    });
  });

  // ========== 5. 关注按钮：toggle ==========
  const followBtn = document.querySelector('.follow-btn');
  if (followBtn) {
    followBtn.addEventListener('click', () => {
      const followed = followBtn.dataset.f === '1';
      if (followed) {
        followBtn.textContent = '关注';
        followBtn.style.background = '#ff2442';
        followBtn.style.color = '#fff';
        followBtn.dataset.f = '0';
      } else {
        followBtn.textContent = '已关注';
        followBtn.style.background = '#f1f1f1';
        followBtn.style.color = '#999';
        followBtn.dataset.f = '1';
      }
    });
  }

  // ========== 6. 互动栏：点赞 / 收藏 toggle ==========
  document.querySelectorAll('.ea-btn').forEach((btn, idx) => {
    btn.addEventListener('click', () => {
      const ic = btn.querySelector('.ea-icon');
      const cnt = btn.querySelector('span:last-child');
      if (!cnt) return;
      const n = parseInt(cnt.textContent, 10);
      if (isNaN(n)) return;
      const liked = btn.dataset.l === '1';
      if (liked) {
        cnt.textContent = n - 1;
        ic.style.color = '';
        btn.dataset.l = '0';
      } else {
        // 仅前两个（赞 / 收藏）允许变色
        if (idx < 2) {
          ic.style.color = idx === 0 ? '#ff2442' : '#fdbc5f';
        }
        cnt.textContent = n + 1;
        btn.dataset.l = '1';
      }
    });
  });

  // ========== 7. 评论小心心 toggle ==========
  document.querySelectorAll('.c-like').forEach((el) => {
    el.addEventListener('click', () => {
      const liked = el.dataset.l === '1';
      const txt = el.textContent.trim();
      const m = txt.match(/(\d+)/);
      if (liked) {
        el.style.color = '';
        el.textContent = '♡ ' + (m ? Math.max(0, parseInt(m[1], 10) - 1) : '赞');
        el.dataset.l = '0';
      } else {
        el.style.color = '#ff2442';
        el.textContent = '♥ ' + (m ? parseInt(m[1], 10) + 1 : 1);
        el.dataset.l = '1';
      }
    });
  });
})();
