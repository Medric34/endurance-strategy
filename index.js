import express from "express";
import fetch from "node-fetch";

const app = express();

/**
 * Route de test (ne pas supprimer)
 */
app.get("/", (req, res) => {
  res.json({
    status: "OK",
    message: "Serveur stratégie opérationnel"
  });
});

/**
 * Route ITS Live – données brutes
 */
app.get("/itslive", async (req, res) => {
  try {
    const response = await fetch(
      "https://api-live.its-live.net/v1/Session/GetRankingWithBestOfAll"
    );

    const data = await response.json();
    res.json(data);

  } catch (error) {
    res.status(500).json({
      error: "Impossible de récupérer les données ITS Live",
      details: error.message
    });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log("Server running on port", PORT);
});
