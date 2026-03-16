const BUILDINGS = [
  { name: 'T', buildTime: 5, rate: 1500 },
  { name: 'P', buildTime: 4, rate: 1000 },
  { name: 'C', buildTime: 10, rate: 2000 },
];

// Calculate earnings for a given build sequence
// Buildings are built sequentially, earning starts after build completes
function calcEarnings(sequence, n) {
  let time = 0;
  let total = 0;
  for (const b of sequence) {
    time += b.buildTime;
    if (time > n) break;
    const operational = n - time;
    total += operational * b.rate;
  }
  return total;
}

// Try all combinations of (t, p, c) buildings built sequentially
// Buildings within a type are identical so order within type doesn't matter
// But order across types does — we try all orderings of the mix
function maxProfit(n) {
  let best = 0;
  const solutions = [];

  // Max possible counts for each building type
  const maxT = Math.floor(n / BUILDINGS[0].buildTime);
  const maxP = Math.floor(n / BUILDINGS[1].buildTime);
  const maxC = Math.floor(n / BUILDINGS[2].buildTime);

  for (let t = 0; t <= maxT; t++) {
    for (let p = 0; p <= maxP; p++) {
      for (let c = 0; c <= maxC; c++) {
        const totalTime = t * 5 + p * 4 + c * 10;
        if (totalTime > n) continue;
        if (t === 0 && p === 0 && c === 0) continue;

        // Try all orderings to find best sequence for this mix
        const earnings = bestOrderEarnings(t, p, c, n);

        if (earnings > best) {
          best = earnings;
          solutions.length = 0;
          solutions.push({ t, p, c });
        } else if (earnings === best && earnings > 0) {
          // Avoid duplicates
          const exists = solutions.some(s => s.t === t && s.p === p && s.c === c);
          if (!exists) solutions.push({ t, p, c });
        }
      }
    }
  }

  // Edge case: n too small to build anything
  if (solutions.length === 0) {
    solutions.push({ t: 0, p: 0, c: 0 });
  }

  return { best, solutions };
}

// For a given count of each building, find the ordering that maximizes earnings
// Greedy: always build the one with highest remaining earnings/time ratio
function bestOrderEarnings(t, p, c, n) {
  let remaining = { T: t, P: p, C: c };
  let time = 0;
  let total = 0;

  const counts = { T: t, P: p, C: c };
  const info = { T: BUILDINGS[0], P: BUILDINGS[1], C: BUILDINGS[2] };

  while (true) {
    let bestChoice = null;
    let bestVal = -1;

    for (const key of ['T', 'P', 'C']) {
      if (remaining[key] <= 0) continue;
      const b = info[key];
      if (time + b.buildTime > n) continue;
      const val = (n - time - b.buildTime) * b.rate;
      if (val > bestVal) {
        bestVal = val;
        bestChoice = key;
      }
    }

    if (!bestChoice) break;

    const b = info[bestChoice];
    time += b.buildTime;
    total += (n - time) * b.rate;
    remaining[bestChoice]--;
  }

  return total;
}

function solve() {
  const input = document.getElementById('timeInput').value.trim();
  const errorEl = document.getElementById('errorMsg');
  const resultSection = document.getElementById('resultSection');

  errorEl.style.display = 'none';

  if (!input) { showError('Please enter a time unit.'); return; }

  const n = parseInt(input, 10);
  if (isNaN(n) || n < 0) { showError('Please enter a valid non-negative integer.'); return; }

  const { best, solutions } = maxProfit(n);

  document.getElementById('resultValue').textContent = `$${best.toLocaleString()}`;

  const list = document.getElementById('solutionsList');
  list.innerHTML = '';

  solutions.forEach((s, i) => {
    const div = document.createElement('div');
    div.className = 'solution-item';
    div.innerHTML = `
      <div class="sol-label">Solution ${i + 1}</div>
      <div class="sol-mix">
        T: <span>${s.t}</span> &nbsp; P: <span>${s.p}</span> &nbsp; C: <span>${s.c}</span>
      </div>
    `;
    list.appendChild(div);
  });

  resultSection.style.display = 'block';
  resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function showError(msg) {
  const el = document.getElementById('errorMsg');
  el.textContent = msg;
  el.style.display = 'block';
}

function loadExample(val) {
  document.getElementById('timeInput').value = val;
  solve();
}

document.getElementById('timeInput').addEventListener('keydown', e => {
  if (e.key === 'Enter') solve();
});