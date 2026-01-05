
-- sessions à ingérer (on ajoute body_json)
CREATE TABLE IF NOT EXISTS sessions_to_fetch (
  session_id TEXT PRIMARY KEY,
  url TEXT NOT NULL,
  params_json TEXT,
  body_json TEXT,          -- <--- NOUVEAU
  fetched BOOLEAN DEFAULT FALSE
);

-- classement final (ajout des colonnes vues dans ton JSON)
CREATE TABLE IF NOT EXISTS final_classification (
  session_id TEXT,
  car_id TEXT,
  number TEXT,             -- ex. "91" (ou ???)
  pos INT,
  class TEXT,
  team TEXT,
  brand TEXT,
  vehicle TEXT,
  drivers TEXT,
  total_lap INT,
  bestlap_ms INT,          -- best_time
  bestlap_no INT,          -- best_time_lap
  last_lap_time_ms INT,    -- lap_time
  gap_first TEXT,
  gap_prev TEXT,
  PRIMARY KEY (session_id, car_id)
);

-- best-of-all par voiture (avec extra_s4 pour 'best_inter_4' qui peut être une vitesse moyenne)
CREATE TABLE IF NOT EXISTS best_of_all (
  session_id TEXT,
  car_id TEXT,
  s1_ms INT,
  s2_ms INT,
  s3_ms INT,
  best_ms INT,
  extra_s4 NUMERIC,
  PRIMARY KEY (session_id, car_id)
);

-- (optionnel) résumé global de session
CREATE TABLE IF NOT EXISTS session_boa (
  session_id TEXT PRIMARY KEY,
  boa JSONB,
  sboa JSONB,
  boa_time INT,
  boa_time_lap INT
);
