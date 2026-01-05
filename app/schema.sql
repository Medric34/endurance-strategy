
-- sessions à ingérer (URL DevTools et params bruts JSON)
CREATE TABLE IF NOT EXISTS sessions_to_fetch (
  session_id TEXT PRIMARY KEY,
  url TEXT NOT NULL,
  params_json TEXT,
  fetched BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS final_classification (
  session_id TEXT,
  car_id TEXT,
  pos INT,
  class TEXT,
  team TEXT,
  drivers TEXT,
  bestlap_ms INT,
  PRIMARY KEY (session_id, car_id)
);

CREATE TABLE IF NOT EXISTS laps (
  session_id TEXT,
  car_id TEXT,
  lap_no INT,
  lap_time_ms INT,
  pit BOOLEAN,
  fcy BOOLEAN,
  sc BOOLEAN,
  PRIMARY KEY (session_id, car_id, lap_no)
);

CREATE TABLE IF NOT EXISTS best_of_all (
  session_id TEXT,
  car_id TEXT,
  s1_ms INT,
  s2_ms INT,
  s3_ms INT,
  best_ms INT,
  PRIMARY KEY (session_id, car_id)
);

CREATE TABLE IF NOT EXISTS indices (
  session_id TEXT,
  car_id TEXT,
  key TEXT,
  value NUMERIC,
  updated_at TIMESTAMP DEFAULT now(),
  PRIMARY KEY (session_id, car_id, key)
);
``

