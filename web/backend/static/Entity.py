from sqlalchemy import Column, DateTime, Integer, String, LargeBinary, ForeignKey, create_engine, Boolean
from sqlalchemy.orm import DeclarativeBase, relationship, Session

from datetime import datetime

SQLALCHEMY_DATABASE_URL = 'sqlite:///web\\backend\\music.db' # ссылка на дб


# создание процесса
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)


class Base(DeclarativeBase): pass


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(30), unique=True, nullable=False)
    password = Column(String(40), nullable=False)
    music_sheet = relationship('MusicSheet', back_populates='user', uselist=True, cascade='all, delete')
    recognized_music_sheet = relationship('RecognizedMusicSheet', back_populates='user', uselist=True, cascade='all, delete')

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class MusicSheet(Base):
    __tablename__ = 'music_sheet'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    music_sheet = Column(LargeBinary, nullable=False)
    rec_sheet_id = Column(Integer, ForeignKey('recognized_music_sheet.id'))
    title = Column(String(70), nullable=False)
    last = Column(Boolean, nullable=False)
    user = relationship('User', back_populates='music_sheet', uselist=False)
    recognized_music_sheet = relationship('RecognizedMusicSheet', back_populates='music_sheet', uselist=False, cascade='all, delete')

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class RecognizedMusicSheet(Base):
    __tablename__ = 'recognized_music_sheet'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    recognized_music = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime, default=datetime.now(), nullable=False)
    music_sheet = relationship('MusicSheet', back_populates='recognized_music_sheet', uselist=True)
    user = relationship('User', back_populates='recognized_music_sheet', uselist=False)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# создание всех таблиц
# Base.metadata.create_all(engine)