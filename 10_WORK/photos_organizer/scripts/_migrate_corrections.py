import sqlite3

DB_PATH = r"E:\PAIOS\10_WORK\photos_organizer\database\photo_index.db"
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

c.execute("DROP TABLE IF EXISTS corrections")
c.execute("""
CREATE TABLE corrections (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    photo_id        INTEGER NOT NULL,
    photo_path      TEXT,
    field           TEXT NOT NULL,
    old_value       TEXT,
    new_value       TEXT,
    reason          TEXT,
    pattern_id      TEXT,
    operator        TEXT DEFAULT 'user',
    created_at      TEXT,
    FOREIGN KEY (photo_id) REFERENCES photos(id)
)
""")
c.execute("CREATE INDEX IF NOT EXISTS idx_corr_photo ON corrections(photo_id)")
c.execute("CREATE INDEX IF NOT EXISTS idx_corr_field ON corrections(field)")
c.execute("CREATE INDEX IF NOT EXISTS idx_corr_pattern ON corrections(pattern_id)")
conn.commit()

c.execute("PRAGMA table_info(corrections)")
cols = c.fetchall()
print("corrections 表新 schema:")
for col in cols:
    print(f"  {col}")
conn.close()
