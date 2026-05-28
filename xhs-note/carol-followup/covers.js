/* ================================================================
   Carol 国际生观察 · 衍生 4 篇 · 首图导出脚本
   - 单张点击下载 / 一键全下
   - html2canvas（CDN）
   ================================================================ */

(function () {
  const RENDER_SCALE = 2;
  const SLEEP_BETWEEN = 250;

  const covers = Array.from(document.querySelectorAll('.cover'));
  const downloadAllBtn = document.getElementById('downloadAll');
  const total = covers.length;

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  async function waitFontsReady() {
    if (document.fonts && document.fonts.ready) {
      try { await document.fonts.ready; } catch (e) {}
    }
  }

  async function renderCover(coverEl, scale = RENDER_SCALE) {
    if (typeof html2canvas !== 'function') {
      throw new Error('html2canvas 未加载，请检查网络。');
    }

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
    return `carol-followup-${num}${name ? '-' + name : ''}.png`;
  }

  async function downloadOne(coverEl) {
    await waitFontsReady();
    const canvas = await renderCover(coverEl);
    const blob = await canvasToBlob(canvas);
    downloadBlob(blob, fileNameOf(coverEl));
  }

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

  // 单张点击：挂在 cover-wrap 上
  document.querySelectorAll('.cover-wrap').forEach((wrap) => {
    const inner = wrap.querySelector('.cover');
    if (!inner) return;
    wrap.addEventListener('click', async () => {
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

  downloadAllBtn.addEventListener('click', downloadAll);

  console.log(
    `%c Carol 衍生 4 篇 · 首图预览 \n%c 已渲染 ${total} 张 · 输出尺寸 1242×1656 (×${RENDER_SCALE}) `,
    'background:#E85A4F;color:#fff;font-weight:700;padding:6px 12px;border-radius:6px 0 0 6px',
    'background:#FAF6EE;color:#2D3D5C;padding:6px 12px;border-radius:0 6px 6px 0'
  );
})();
