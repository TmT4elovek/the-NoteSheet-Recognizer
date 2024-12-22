from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import DeclarativeBase, Relationship

from .config import SQLALCHEMY_DATABASE_URL


# создание процесса
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)


class Base(DeclarativeBase): pass


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(30), unique=True, nullable=False)
    password = Column(String(40), nullable=False)
    music_sheet = Relationship('MusicSheet', backref='user', uselist=False)


class MusicSheet(Base):
    __tablename__ = 'music_sheet'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    music_sheet = Column(String, nullable=False) # имя файла в каталоге music_sheets
    title = Column(String(70), nullable=False)
    user = Relationship('user', back_populates='music_sheets')
    music_sheet = Relationship('recognized_music_sheet', backref='music_sheet', uselist=False)


class RecognizedMusicSheet(Base):
    __tablename__ = 'recognized_music_sheet'

    id = Column(Integer, primary_key=True)
    recognized_music = Column(String, nullable=False) # имя файла в каталоге audio
    sheet_id = Column(Integer, ForeignKey('music_sheet.id'))
    music_sheet = Relationship('music_sheet', backref='recognized_music_sheet', uselist=False)


# создание всех таблиц
Base.metadata.create_all(engine) 