from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import DeclarativeBase, relationship, Session

SQLALCHEMY_DATABASE_URL = 'sqlite:///D:\\Programming\mospredp\\the-NoteSheet-Recognizer\\web\\backend\\music.db' # ссылка на дб


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
    music_sheets = relationship('MusicSheet', back_populates='user', uselist=False, cascade='all, delete')

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class MusicSheet(Base):
    __tablename__ = 'music_sheet'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    music_sheet = Column(String, nullable=False) # имя файла в каталоге music_sheets
    title = Column(String(70), nullable=False)
    user = relationship('User', back_populates='music_sheets', uselist=True)
    recognized_music_sheet = relationship('RecognizedMusicSheet', back_populates='music_sheet', uselist=False, cascade='all, delete')

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class RecognizedMusicSheet(Base):
    __tablename__ = 'recognized_music_sheet'

    id = Column(Integer, primary_key=True)
    recognized_music = Column(String, nullable=False) # имя файла в каталоге audio
    sheet_id = Column(Integer, ForeignKey('music_sheet.id'))
    music_sheet = relationship('MusicSheet', back_populates='recognized_music_sheet', uselist=False)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# создание всех таблиц
# Base.metadata.create_all(engine)