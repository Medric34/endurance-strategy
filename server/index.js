
// server/index.js
import express from 'express';
import fetch from 'node-fetch';
import cors from 'cors';

const app = express();
const ORIGIN = process.env.ALLOWED_ORIGIN || '*';
const ITS_BASE = process.env.ITS_BASE || 'https://www.its-live.net';

app.use(cors({ origin: ORIGIN }));
app.use(express.json({ limit: '1mb' }));

// Route d'ingestion (Plan B Tampermonkey)
const STORE = { last: null, updatedAt: null };
app.post('/api/ingest', (req, res) => {
  STORE.last = req.body;
  STORE.updatedAt = new Date().toISOString();
  res.json({ ok: true, updatedAt: STORE.updatedAt });
});
app.get('/api/ingest', (req, res) => {
  res.json({ updatedAt: STORE.updatedAt, payload: STORE.last });
});

// Route "pull" directe (peut échouer si ITS renvoie HTML)
app.get('/api/tte/:season/:event/:session/ranking', async (req, res) => {
  try {
    const { season, event, session } = req.params;

    // ⚠️ Vérifie la vraie URL dans DevTools → Network.
    const url = `${ITS_BASE}/live/tte/${season}/${event}/${session}/getrankingwithbestofall`;

    const upstream = await fetch(url, {
      headers: {
        'Accept': 'application/json,text/plain,*/*',
        'User-Agent': 'EnduranceStrategy/1.0',
        'Referer': `${ITS_BASE}/live/tte/${season}/${event}/${session}`
      },
      redirect: 'follow'
    });

    const ct = upstream.headers.get('content-type') || '';
    const status = upstream.status;

    if (!upstream.ok) {
      const text = await upstream.text();
      console.error('Upstream not OK:', status, ct, text.slice(0, 400));
      return res.status(status).json({
        error: 'upstream_error',
        status,
        contentType: ct,
        message: 'Upstream returned non-OK status',
        sample: text.slice(0, 400)
      });
    }

    if (ct.includes('application/json')) {
      const raw = await upstream.json();
      const rows = (raw.ranking || []).map(v => ({
        number: v.number,
        pos: v.pos,
        lap_time_ms: v.lap_time,
        s1_ms: v.inter_1,
        s2_ms: v.inter_2,
        s3_ms: v.inter_3,
        best_ms: v.best_time,
        ideal_ms: v.ideal_time,
        team: v.team,
        cat: v.cat
      }));

      return res.json({
        updatedAt: new Date().toISOString(),
        boa: raw.boa ?? null,
        boaTime_ms: raw.boaTime ?? null,
        boaTimeLap: raw.boaTimeLap ?? null,
        rows
      });
    } else {
      const text = await upstream.text();
      console.error('Expected JSON but got HTML:', status, ct);
      return res.status(502).json({
        error: 'server_error',
        status,
        contentType: ct,
        message: 'Upstream returned HTML instead of JSON',
        sample: text.slice(0, 400)
      });
    }
  } catch (e) {
    console.error('Server error:', e);
    res.status(500).json({ error: 'server_error', message: e.message });
  }
});

const PORT = process.env.PORT || 10000;
app.listen(PORT, () => console.log(`Backend up on :${PORT}`));
