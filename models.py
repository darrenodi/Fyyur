from flask import Flask
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime


app = Flask(__name__)
db = SQLAlchemy(app)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    looking_for_talent = db.Column(db.Boolean,default=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Shows', backref='venues', lazy=True)

    def __repr__(self):
       return f'<Venue "{self.name}">'
    # TODO: implement any missing fields, as a database migration using Flask-Migrate DONE

class Artist(db.Model):
    __tablename__ = 'artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    looking_for_talent = db.Column(db.Boolean,default=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Shows', backref='artists', lazy=True)

    def __repr__(self):
       return f'<Artist "{self.name}">'


    # TODO: implement any missing fields, as a database migration using Flask-Migrate DONE

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration. DONE
class Shows(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable = False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable = False)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
       return f'<Show "{self.id}">'

class Available(db.Model):
    __tablename__ = 'availability'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable = False)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
       return f'<Availability "{self.id}">'

db.create_all()