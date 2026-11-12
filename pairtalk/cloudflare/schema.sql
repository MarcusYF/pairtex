-- Derived from html-slide by Yanwei Sun (https://github.com/Yanwei-Sun/html-slide); see NOTICE.md.
-- PairTalk's shared review site: comments with boxes and images, and shared script edits. `pairtalk publish` applies it.
CREATE TABLE IF NOT EXISTS comments (
  cid      TEXT PRIMARY KEY,
  deck     TEXT,
  n        INTEGER,
  k        INTEGER,
  sid      TEXT,
  title    TEXT,
  author   TEXT,
  text     TEXT,
  created  TEXT,
  status   TEXT NOT NULL DEFAULT 'open',
  reply    TEXT NOT NULL DEFAULT '',
  resolved TEXT NOT NULL DEFAULT '',
  box      TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS comments_deck_created ON comments (deck, created);

CREATE TABLE IF NOT EXISTS comment_images (
  cid   TEXT NOT NULL,
  i     INTEGER NOT NULL,
  mime  TEXT NOT NULL,
  w     INTEGER,
  h     INTEGER,
  bytes INTEGER NOT NULL,
  data  BLOB NOT NULL,
  PRIMARY KEY (cid, i)
);

CREATE TABLE IF NOT EXISTS script_edits (
  eid      TEXT PRIMARY KEY,
  deck     TEXT NOT NULL,
  sid      TEXT NOT NULL,
  k        INTEGER NOT NULL,
  text     TEXT,
  orig     TEXT NOT NULL DEFAULT '',
  sent     TEXT,
  updated  TEXT NOT NULL,
  status   TEXT NOT NULL DEFAULT 'open',
  applied  TEXT NOT NULL DEFAULT '',
  author   TEXT NOT NULL DEFAULT ''
);

