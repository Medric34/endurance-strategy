
// web/app.js
const API = (window.API_BASE || '').trim() || 'https://<TON-BACKEND>.onrender.com';
const PATH = '/api/tte/2025/magnycoursfinale/23/ranking'; // change si besoin

const fmt = (ms) => (ms == null || ms < 0) ? '' : (ms / 1000).toFixed(3);

async function tick() {
  try {
    const r = await fetch(`${API}${PATH}`);
    const data = await r.json();

    const meta = document.querySelector('#meta');
    meta.textContent = `MAJ: ${data.updatedAt} | BOA: ${fmt(data.boaTime_ms)}s (Lap ${data.boaTimeLap})`;

    const tbody = document.querySelector('#tbl tbody');
    tbody.innerHTML = (data.rows || [])
      .sort((a,b) => (a.pos ?? 9999) - (b.pos ?? 9999))
      .map(v => `
        <tr>
          <td>${v.number ?? ''}</td>
          <td>${v.pos ?? ''}</td>
          <td>${fmt(v.lap_time_ms)}</td>
          <td>${fmt(v.s1_ms)}</td>
          <td>${fmt(v.s2_ms)}</td>
          <td>${fmt(v.s3_ms)}</td>
          <td>${fmt(v.best_ms)}</td>
          <td>${fmt(v.ideal_ms)}</td>
          <td>${v.team ?? ''}</td>
          <td>${v.cat ?? ''}</td>
        </tr>`).join('');
  } catch(e) {
    console.error(e);
  }
}

// poll toutes les 3 s (ajuste selon charge/latence Render)
setInterval(tick, 3000);
tick();

