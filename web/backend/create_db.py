from flask import Flask
import os

from static.Entity import db, User, MusicSheet

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'music.db')

db.init_app(app)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()