function computeWater(heights) {
  const n = heights.length;
  if (n === 0) return { total: 0, waterAt: [] };

  const leftMax = new Array(n).fill(0);
  const rightMax = new Array(n).fill(0);

  leftMax[0] = heights[0];
  for (let i = 1; i < n; i++) leftMax[i] = Math.max(leftMax[i - 1], heights[i]);

  rightMax[n - 1] = heights[n - 1];
  for (let i = n - 2; i >= 0; i--) rightMax[i] = Math.max(rightMax[i + 1], heights[i]);

  let total = 0;
  const waterAt = new Array(n).fill(0);
  for (let i = 0; i < n; i++) {
    waterAt[i] = Math.max(0, Math.min(leftMax[i], rightMax[i]) - heights[i]);
    total += waterAt[i];
  }

  return { total, waterAt };
}

function renderSVG(heights, waterAt) {
  const n = heights.length;
  const maxH = Math.max(...heights, ...waterAt.map((w, i) => w + heights[i]), 1);
  const cellW = Math.max(44, Math.min(64, Math.floor(680 / n)));
  const cellH = 36;
  const svgW = cellW * n + 2;
  const svgH = cellH * maxH + 20;
  const ns = 'http://www.w3.org/2000/svg';

  const svg = document.createElementNS(ns, 'svg');
  svg.setAttribute('width', svgW);
  svg.setAttribute('height', svgH);
  svg.setAttribute('viewBox', `0 0 ${svgW} ${svgH}`);

  const bg = document.createElementNS(ns, 'rect');
  bg.setAttribute('width', svgW);
  bg.setAttribute('height', svgH);
  bg.setAttribute('fill', '#0a0e1a');
  svg.appendChild(bg);

  for (let col = 0; col < n; col++) {
    const blockH = heights[col];
    const waterH = waterAt[col];
    const totalH = blockH + waterH;
    const x = col * cellW + 1;

    for (let row = maxH; row > totalH; row--) {
      const rect = document.createElementNS(ns, 'rect');
      rect.setAttribute('x', x);
      rect.setAttribute('y', (maxH - row) * cellH + 1);
      rect.setAttribute('width', cellW - 1);
      rect.setAttribute('height', cellH - 1);
      rect.setAttribute('fill', '#1a2535');
      rect.setAttribute('rx', '2');
      svg.appendChild(rect);
    }

    for (let row = totalH; row > blockH; row--) {
      const rect = document.createElementNS(ns, 'rect');
      rect.setAttribute('x', x);
      rect.setAttribute('y', (maxH - row) * cellH + 1);
      rect.setAttribute('width', cellW - 1);
      rect.setAttribute('height', cellH - 1);
      rect.setAttribute('fill', '#00aaee');
      rect.setAttribute('fill-opacity', '0.82');
      rect.setAttribute('rx', '2');
      svg.appendChild(rect);
    }

    for (let row = blockH; row > 0; row--) {
      const rect = document.createElementNS(ns, 'rect');
      rect.setAttribute('x', x);
      rect.setAttribute('y', (maxH - row) * cellH + 1);
      rect.setAttribute('width', cellW - 1);
      rect.setAttribute('height', cellH - 1);
      rect.setAttribute('fill', '#e8b400');
      rect.setAttribute('rx', '2');
      svg.appendChild(rect);
    }

    const label = document.createElementNS(ns, 'text');
    label.setAttribute('x', x + (cellW - 1) / 2);
    label.setAttribute('y', svgH - 4);
    label.setAttribute('text-anchor', 'middle');
    label.setAttribute('fill', '#64748b');
    label.setAttribute('font-size', '10');
    label.setAttribute('font-family', 'Space Mono, monospace');
    label.textContent = heights[col];
    svg.appendChild(label);
  }

  return svg;
}

function solve() {
  const input = document.getElementById('heightInput').value.trim();
  const errorEl = document.getElementById('errorMsg');
  const resultSection = document.getElementById('resultSection');

  errorEl.style.display = 'none';

  if (!input) { showError('Please enter block heights.'); return; }

  const heights = input.split(',').map(s => Number(s.trim()));

  if (heights.some(isNaN)) { showError('Invalid input. Use comma-separated numbers.'); return; }
  if (heights.some(h => h < 0)) { showError('All heights must be >= 0.'); return; }

  const { total, waterAt } = computeWater(heights);

  document.getElementById('resultValue').textContent = `${total} unit${total !== 1 ? 's' : ''}`;

  const svgWrap = document.getElementById('svgWrap');
  svgWrap.innerHTML = '';
  svgWrap.appendChild(renderSVG(heights, waterAt));

  resultSection.style.display = 'block';
  resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function showError(msg) {
  const el = document.getElementById('errorMsg');
  el.textContent = msg;
  el.style.display = 'block';
}

function loadExample(val) {
  document.getElementById('heightInput').value = val;
  solve();
}

document.getElementById('heightInput').addEventListener('keydown', e => {
  if (e.key === 'Enter') solve();
});