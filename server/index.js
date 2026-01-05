
// server/index.js
import express from 'express';
import fetch from 'node-fetch';
import cors from 'cors';

const app = express();

// CORS: n'autorise que ton domaine frontend (à changer après déploi)
const ALLOWED_ORIGIN = process.env.ALLOWED_ORIGIN || '*';
app.use(cors({ origin: ALLOWED_ORIGIN }));

// Sécurité basique
app.use(express.json({ limit: '1mb' }));

// Exemple d'URL ITS (à adapter à l’endpoint exact que tu vois dans DevTools)
// Idéalement, tu stockes la base dans une variable d'environnement Render.
const ITS_BASE = process.env.ITS_BASE || 'https://www.its-live.net';

// Route qui récupère et “nettoie” le JSON
app.get('/api/tte/:season/:event/:session/ranking', async (req, res) => {
  try {
    const { season, event, session } = req.params;

    // IMPORTANT: remplace par le chemin exact de ta requête réelle observée côté navigateur.
    // Ex: `${ITS_BASE}/live/tte/${season}/${event}/${session}/getrankingwithbestofall`
    const url = `${ITS_BASE}/live/tte/${season}/${event}/${session}/getrankingwithbestofall`;

    // Certains endpoints exigent des headers (ex: Referer, Accept). Ajuste au besoin.
    const r = await fetch(url, {
      headers: {
        'Accept': 'application/json,text/plain,*/*',
        'User-Agent': 'Render-POC/1.0',
        'Referer': `${ITS_BASE}/live/tte/${season}/${event}/${session}`,
      }
    });

    if (!r.ok) {
      return res.status(r.status).json({ error: `Upstream error ${r.status}` });
    }

    const raw = await r.json();

    // Normalisation: extraire N°, Lap, S1/S2/S3, Best, Ideal, Team, Cat
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

    const response = {
      updatedAt: new Date().toISOString(),
      boa: raw.boa ?? null,
      boaTime_ms: raw.boaTime ?? null,
      boaTimeLap: raw.boaTimeLap ?? null,
      rows
    };

    res.json(response);
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: 'server_error', message: e.message });
  }
});

const PORT = process.env.PORT || 10000;
app.listen(PORT, () => console.log(`Backend up on :${PORT}`));

