from sqlalchemy import create_engine
from static.Entity import MusicSheet, User, RecognizedMusicSheet, SQLALCHEMY_DATABASE_URL
from sqlalchemy.orm import Session

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

with Session(engine) as db:
    with open(r'web\backend\aud.mp3', 'rb') as a:
        a = a.read()
    sheet = RecognizedMusicSheet(recognized_music=a, user_id=1)
    db.add(sheet)
    db.commit()