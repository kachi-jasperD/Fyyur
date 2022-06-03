#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import datetime
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
# TODO: connect to a local postgresql database
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
  __tablename__ = 'shows'

  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id', ondelete='CASCADE'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id', ondelete='CASCADE'), nullable=False)
  date_time = db.Column(db.DateTime(), default=datetime.datetime.now())

  def __repr__(self):
        return f'<Show ID: {self.id}, artist_id: {self.artist_id}, venue_id: {self.venue_id}, date_time: {self.date_time}>'



class Venue(db.Model):
# TODO: implement any missing fields, as a database migration using Flask-Migrate
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()),nullable=False)
    website_link = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    venues_show_mapping = db.relationship('Show', backref=db.backref('venue',lazy=True, cascade="all, delete"))

    def __repr__(self):
        return f'<Venue ID: {self.id}, name: {self.name}, city: {self.city}, state: {self.state}, address: {self.address}, phone: {self.phone}, image_link: {self.image_link}, facebook_link: {self.facebook_link}, genres: {self.genres}, website_link: {self.website_link}, seeking_talent: {self.seeking_talent}, seeking_description: {self.seeking_description}>'

    

class Artist(db.Model):
# TODO: implement any missing fields, as a database migration using Flask-Migrate
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()),nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    show_artist_mapping = db.relationship('Show', backref=db.backref('artist',lazy=True, cascade="all, delete"))

    def __repr__(self):
        return f'<Artist ID: {self.id}, name: {self.name} city: {self.city}, state: {self.state}, phone: {self.phone}, genres: {self.genres}, image_link: {self.image_link}, facebook_link: {self.facebook_link}, website_link: {self.website_link}, seeking_venue: {self.seeking_venue}, seeking_description: {self.seeking_description}>'

