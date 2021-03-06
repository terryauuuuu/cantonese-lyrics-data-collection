DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;

CREATE TABLE record (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  singer TEXT NOT NULL,
  songName TEXT NOT NULL,
  start FLOAT NOT NULL,
  end FLOAT NOT NULL,
  lyrics TEXT NOT NULL,
  isLyrics BOOLEAN NOT NULL,
);

CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);