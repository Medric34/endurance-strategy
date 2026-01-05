import express from "express";
import fetch from "node-fetch";

const app = express();

/**
 * ============================
 * ROUTE 1 — TEST DU SERVEUR
 * ============================
 * URL : /
 * Sert uniquement à vérifier que le serveur fonctionne
 */
app.get("/", (req, res) => {
  res.json({
    status: "OK",
    message: "Serveur stratégie opérationnel"
  });
});

/**
 * ============================
 * ROUTE 2 — DONNÉES ITS LIVE
 * ============================
 * URL : /itslive
 * Cette route va :
 * 1. Appeler ITS Live
 * 2. Récupérer les chronos
 * 3. Les renvoyer tels quels
 */
app.get("/itslive", async (req, res) => {
  try {
    const response = await fetch(
      "https://api-live.its-live.net/v1/Session/GetRankingWithBestOfAll",
      {
        headers: {
          // On se fait passer pour un navigateur
          "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
          "Accept": "application/json",
          "Referer": "https://www.its-live.net/"
        }
      }
    );

    // On lit la réponse comme du texte
    const text = await response.text();

    // Sécurité : ITS Live renvoie parfois du HTML
    if (!text.startsWith("{") && !text.startsWith("[")) {
      return res.status(500).json({
        error: "ITS Live ne renvoie pas du JSON",
        preview: text.substring(0, 300)
      });
    }

    // Conversion en JSON
    const data = JSON.parse(text);

    // On renvoie les données
    res.json(data);

  } catch (error) {
    res.status(500).json({
      error: "Impossible de récupérer les données ITS Live",
      details: error.message
    });
  }
});

/**
 * ============================
 * DÉMARRAGE DU SERVEUR
 * ============================
 */
const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log("Server running on port", PORT);
});
