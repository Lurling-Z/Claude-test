/* ================================================================
   Carol 国际生观察 · 12 张封面图导出脚本
   - 单张点击下载
   - 一键下载全部 PNG
   - 使用 html2canvas（CDN 引入）
   ================================================================ */

(function () {
  const RENDER_SCALE = 2;          // 1242 * 2 = 2484，超清；如果太大改成 1
  const SLEEP_BETWEEN = 250;       // 每张之间的间隔（毫秒），让浏览器喘口气

  const covers = Array.from(document.querySelectorAll('.cover'));
  const downloadAllBtn = document.getElementById('downloadAll');
  const total = covers.length;

  // ==================== 工具：sleep ====================
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  // ==================== 等待字体加载 ====================
  async function waitFontsReady() {
    if (document.fonts && document.fonts.ready) {
      try { await document.fonts.ready; } catch (e) {}
    }
  }

  // ==================== 渲染单张 ====================
  // 因为 .cover 在预览里是 transform: scale(0.5) 的，
  // 我们需要克隆一份去掉 scale，离屏渲染成原始 1242×1656 大小。
  async function renderCover(coverEl, scale = RENDER_SCALE) {
    if (typeof html2canvas !== 'function') {
      throw new Error('html2canvas 未加载，请检查网络。');
    }

    // 创建一个绝对定位、不可见的离屏舞台
    const stage = document.createElement('div');
    stage.style.cssText = `
      position: fixed;
      left: -99999px;
      top: 0;
      width: 1242px;
      height: 1656px;
      z-index: -1;
      pointer-events: none;
    `;
    const clone = coverEl.cloneNode(true);
    clone.style.transform = 'none';
    clone.style.margin = '0';
    clone.style.position = 'static';
    clone.style.width = '1242px';
    clone.style.height = '1656px';
    stage.appendChild(clone);
    document.body.appendChild(stage);

    let canvas;
    try {
      canvas = await html2canvas(clone, {
        backgroundColor: null,
        scale: scale,
        useCORS: true,
        allowTaint: false,
        logging: false,
        width: 1242,
        height: 1656,
        windowWidth: 1242,
        windowHeight: 1656,
      });
    } finally {
      document.body.removeChild(stage);
    }
    return canvas;
  }

  // ==================== 下载工具 ====================
  function canvasToBlob(canvas) {
    return new Promise((resolve) => {
      canvas.toBlob((blob) => resolve(blob), 'image/png', 0.95);
    });
  }

  function downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  function fileNameOf(coverEl) {
    const num = coverEl.dataset.num || '00';
    const name = coverEl.dataset.name || '';
    return `carol-xhs-${num}${name ? '-' + name : ''}.png`;
  }

  // ==================== 单张下载 ====================
  async function downloadOne(coverEl) {
    await waitFontsReady();
    const canvas = await renderCover(coverEl);
    const blob = await canvasToBlob(canvas);
    downloadBlob(blob, fileNameOf(coverEl));
  }

  // ==================== 全部下载 ====================
  async function downloadAll() {
    if (downloadAllBtn.disabled) return;
    downloadAllBtn.disabled = true;
    const originalText = downloadAllBtn.textContent;
    await waitFontsReady();

    try {
      for (let i = 0; i < total; i++) {
        downloadAllBtn.textContent = `导出中… ${i + 1} / ${total}`;
        const cover = covers[i];
        try {
          const canvas = await renderCover(cover);
          const blob = await canvasToBlob(canvas);
          downloadBlob(blob, fileNameOf(cover));
        } catch (err) {
          console.error(`第 ${i + 1} 张导出失败：`, err);
        }
        await sleep(SLEEP_BETWEEN);
      }
      downloadAllBtn.textContent = '✓ 全部已下载';
      setTimeout(() => {
        downloadAllBtn.textContent = originalText;
        downloadAllBtn.disabled = false;
      }, 2000);
    } catch (e) {
      alert('导出失败：' + (e && e.message ? e.message : e));
      downloadAllBtn.textContent = originalText;
      downloadAllBtn.disabled = false;
    }
  }

  // ==================== 单张点击下载（包裹层伪元素 + 实际监听包裹层） ====================
  // 因为 cover 自身有 scale(0.5) + 负 margin，事件区域不直观，
  // 我们把点击监听挂在 .cover-wrap 上，但只在点到伪元素 ::after 区域时触发。
  // 这里采取更稳妥方式：直接给 cover-wrap 加点击，提示用户「点击下载这一张」。
  document.querySelectorAll('.cover-wrap').forEach((wrap) => {
    const inner = wrap.querySelector('.cover');
    if (!inner) return;
    wrap.style.cursor = 'pointer';
    wrap.addEventListener('click', async (e) => {
      // 防止误触正在下载所有的过程
      if (downloadAllBtn.disabled) return;
      const cap = wrap.querySelector('figcaption');
      const oldCap = cap ? cap.textContent : '';
      if (cap) cap.textContent = '导出中…';
      try {
        await downloadOne(inner);
        if (cap) cap.textContent = '✓ 已下载';
      } catch (err) {
        console.error(err);
        if (cap) cap.textContent = '✗ 失败';
      }
      setTimeout(() => { if (cap) cap.textContent = oldCap; }, 1600);
    });
  });

  // ==================== 主按钮 ====================
  downloadAllBtn.addEventListener('click', downloadAll);

  // ==================== 启动信息 ====================
  console.log(
    `%c Carol 国际生观察 · 12 张封面预览 \n%c 已渲染 ${total} 张封面，输出尺寸 1242×1656 (×${RENDER_SCALE}) `,
    'background:#E85A4F;color:#fff;font-weight:700;padding:6px 12px;border-radius:6px 0 0 6px',
    'background:#FAF6EE;color:#2D3D5C;padding:6px 12px;border-radius:0 6px 6px 0'
  );
})();
