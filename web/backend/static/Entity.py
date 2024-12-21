from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(30), nullable=False)


class MusicSheet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(70), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id') , nullable=False)
    user = db.relationship('User', backref=db.backref('music_sheets', lazy=True))


class RecognisedMusicSheet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sheet_id = db.Column(db.Integer, db.ForeignKey('music_sheet.id'), nullable=False)