#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from distutils.log import error
import json
from tkinter import CASCADE, N
from unicodedata import name
import dateutil.parser
import babel
from flask import render_template, request, Response, flash, redirect, session, url_for
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import PrimaryKeyConstraint
from forms import *
from flask import abort
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import PickleType
import logging
from model import Show, Venue, Artist, db, app



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  
  data=[]
  venue_db = Venue.query.distinct(Venue.city, Venue.state).all()
  for item in venue_db:
    venues = []
    venue_info = Venue.query.filter(Venue.state == item.state, Venue.city == item.city).all()
  
    for venue in venue_info:
        info = {
            'city' : venue.city,
            'state' : venue.state,
            'id' : venue.id,
            'name' : venue.name,
            'num_upcoming_shows' : Show.query.filter(Show.date_time > datetime.now(), Show.venue_id==venue.id).count()
        }
        venues.append(info)
  
    group_venues = {
        'city' : item.city,
        'state' : item.state,
        'venues' : venues
    }
  
    data.append(group_venues)
  return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  posts = Venue.query.filter(Venue.name.ilike(f"%{request.form.get('search_term','')}%")).all()
  count_of_get_venue_by_name = len(posts)

  data = []
 
  for venue in posts:
    info = {
      'id' : venue.id,
      'name' : venue.name,
      'num_upcoming_shows' : Show.query.filter(db.and_(Show.date_time > datetime.now().strftime("%Y-%m-%d %H:%M"), Show.venue_id == venue.id)).count()
    }
    data.append(info)

  

  response={
    "count": count_of_get_venue_by_name,
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>', methods=['GET'])
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  get_venue_by_id = Venue.query.get(venue_id)
  past_shows = []
  upcoming_shows = []
  past = db.session.query(Show).join(Artist).filter(Show.date_time < datetime.now().strftime("%Y-%m-%d %H:%M"), Show.venue_id == venue_id).all()
  for show in past:
    past_show = {
      'artist_id' : show.artist_id,
      'artist_name' : show.artist.name,
      'artist_image_link' : show.artist.image_link,
      'start_time' : str(show.date_time)
    }
    past_shows.append(past_show)
 
  upcoming = db.session.query(Show).join(Artist).filter(Show.date_time > datetime.now().strftime("%Y-%m-%d %H:%M"), Show.venue_id == venue_id).all()
  for show in upcoming:
    upcoming_show = {
      'artist_id' : show.artist_id,
      'artist_name' : show.artist.name,
      'artist_image_link' : show.artist.image_link,
      'start_time' : str(show.date_time)
    }
    upcoming_shows.append(upcoming_show)

  data1={
    "id": get_venue_by_id.id,
    "name": get_venue_by_id.name,
    "genres": get_venue_by_id.genres,
    "address": get_venue_by_id.address,
    "city": get_venue_by_id.city,
    "state": get_venue_by_id.state,
    "phone": get_venue_by_id.phone,
    "website": get_venue_by_id.website_link,
    "facebook_link": get_venue_by_id.facebook_link,
    "seeking_talent": get_venue_by_id.seeking_talent,
    "seeking_description": get_venue_by_id.seeking_description,
    "image_link": get_venue_by_id.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  return render_template('pages/show_venue.html', venue=data1)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm(request.form)
  if form.validate():
    try:
      venue_name = request.form['name']
      venue_city = request.form['city']
      venue_state = request.form['state']
      venue_address = request.form['address']
      venue_phone = request.form['phone']
      venue_image_link = request.form['image_link']
      venue_facebook_link = request.form['facebook_link']
      venue_genres = request.form['genres']
      venue_website_link = request.form['website_link']
      venue_seeking_talent  = True if request.form['seeking_talent'] else False
      venue_seeking_description = request.form['seeking_description']
      new_venue = Venue(name=venue_name, city=venue_city, state=venue_state, phone=venue_phone, address=venue_address, image_link=venue_image_link, facebook_link=venue_facebook_link, genres=venue_genres, website_link=venue_website_link, seeking_talent=venue_seeking_talent, seeking_description=venue_seeking_description)
      db.session.add(new_venue)
      db.session.commit()
       # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
      error = True
      flash('An error occurred. Venue ' + venue_name + ' could not be listed.')
      db.session.rollback()
      abort(400)
    finally:
      db.session.close()
  else:
    return render_template('forms/new_venue.html', form=form)
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  try:
    get_venue_by_id = Venue.query.get(venue_id)
    db.session.delete(get_venue_by_id)
    db.session.commit()
    flash('Venue ' + get_venue_by_id.name + ' successfully deleted.')
  except:
    error =True
    flash('Venue ' + get_venue_by_id.name + ' could not be deleted.')
    db.session.rollback()
    abort(400)
  finally:
      db.session.close()
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=[]
  artist_db = Artist.query.all()
  for row in artist_db:
    info = {
            'id' : row.id,
            'name' : row.name
        }
    data.append(info)
  return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  posts = Artist.query.filter(Artist.name.ilike(f"%{request.form.get('search_term','')}%")).all()
  count_of_get_artist_by_name = len(posts)
  data = []

  for artist in posts:
    info = {
      'id' : artist.id,
      'name' : artist.name,
      'num_upcoming_shows' : Show.query.filter(db.and_(Show.date_time > datetime.now().strftime("%Y-%m-%d %H:%M"), Show.artist_id == artist.id)).count()
    }
    data.append(info)

  response={
    "count": count_of_get_artist_by_name,
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>', methods=['GET'])
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  get_artist_by_id = Artist.query.get(artist_id)
  past_shows = []
  upcoming_shows = []
  past = db.session.query(Show).join(Venue).filter(Show.date_time < datetime.now().strftime("%Y-%m-%d %H:%M"), Show.artist_id == artist_id).all()
  for show in past:
    past_show = {
      'venue_id' : show.venue_id,
      'venue_name' : show.venue.name,
      'venue_image_link' : show.venue.image_link,
      'start_time' : str(show.date_time)
    }
    past_shows.append(past_show)
 
  upcoming = db.session.query(Show).join(Venue).filter(Show.date_time > datetime.now().strftime("%Y-%m-%d %H:%M"), Show.artist_id == artist_id).all()
  for show in upcoming:
    upcoming_show = {
      'venue_id' : show.venue_id,
      'venue_name' : show.venue.name,
      'venue_image_link' : show.venue.image_link,
      'start_time' : str(show.date_time)
    }
    upcoming_shows.append(upcoming_show)
  data1={
    "id": artist_id,
    "name": get_artist_by_id.name,
    "genres": get_artist_by_id.genres,
    "city": get_artist_by_id.city,
    "state": get_artist_by_id.state,
    "phone": get_artist_by_id.phone,
    "website": get_artist_by_id.website_link,
    "facebook_link": get_artist_by_id.facebook_link,
    "seeking_venue": get_artist_by_id.seeking_venue,
    "seeking_description": get_artist_by_id.seeking_description,
    "image_link": get_artist_by_id.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  
  return render_template('pages/show_artist.html', artist=data1)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  get_artist_by_id = Artist.query.get(artist_id)
  genres_list = []
  genres_list.append(get_artist_by_id.genres)
  artist={
    "id": artist_id,
    "name": get_artist_by_id.name,
    "genres": genres_list,
    "city": get_artist_by_id.city,
    "state": get_artist_by_id.state,
    "phone": get_artist_by_id.phone,
    "website": get_artist_by_id.website_link,
    "facebook_link": get_artist_by_id.facebook_link,
    "seeking_venue": get_artist_by_id.seeking_venue,
    "seeking_description": get_artist_by_id.seeking_description,
    "image_link": get_artist_by_id.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)
  get_artist_by_id = Artist.query.get(artist_id)
  try:
      
    get_artist_by_id.name = request.form['name']
    get_artist_by_id.city = request.form['city']
    get_artist_by_id.state = request.form['state']
    get_artist_by_id.phone = request.form['phone']
    get_artist_by_id.genres=request.form.getlist('genres', type=str)
    get_artist_by_id.facebook_link = request.form['facebook_link']
    get_artist_by_id.image_link = request.form['image_link']
    get_artist_by_id.website_link = request.form['website_link']
    get_artist_by_id.seeking_venue = True if request.form['seeking_venue'] else False
    get_artist_by_id.seeking_description = request.form['seeking_description']
    db.session.commit()
    flash('Artist ' + request.form['name']+ ' successfully updated.')
  except:
    error =True
    flash('An error occurred. Artist ' + get_artist_by_id.name + ' could not be updated.')
    db.session.rollback()
    abort(400)
  finally:
    db.session.close()
  
  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  get_venue_by_id = Venue.query.get(venue_id)
  genres_list = []
  genres_list.append(get_venue_by_id.genres)
  venue={
    "id": venue_id,
    "name": get_venue_by_id.name,
    "genres": genres_list,
    "address": get_venue_by_id.address,
    "city": get_venue_by_id.city,
    "state": get_venue_by_id.state,
    "phone": get_venue_by_id.phone,
    "website": get_venue_by_id.website_link,
    "facebook_link": get_venue_by_id.facebook_link,
    "seeking_talent": get_venue_by_id.seeking_talent,
    "seeking_description": get_venue_by_id.seeking_description,
    "image_link": get_venue_by_id.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  try:
    get_venue_by_id = Venue.query.get(venue_id)
    get_venue_by_id.name = request.form['name']
    get_venue_by_id.city = request.form['city']
    get_venue_by_id.state = request.form['state']
    get_venue_by_id.address = request.form['address']
    get_venue_by_id.phone = request.form['phone']
    get_venue_by_id.image_link = request.form['image_link']
    get_venue_by_id.facebook_link = request.form['facebook_link']
    get_venue_by_id.genres = request.form['genres']
    get_venue_by_id.website_link = request.form['website_link']
    get_venue_by_id.seeking_talent = True if request.form['seeking_talent'] else False
    get_venue_by_id.seeking_descriptione = request.form['seeking_description']
    db.session.commit()
    flash('Venue ' + get_venue_by_id.name + ' successfully updated.')
  except:
    error =True
    flash('An error occurred. Venue ' + get_venue_by_id.name + ' could not be updated.')
    db.session.rollback()
    abort(400)
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
# called upon submitting the new artist listing form
# TODO: insert form data as a new Venue record in the db, instead
# TODO: modify data to be the data object returned from db insertion
# TODO: on unsuccessful db insert, flash an error instead.
# e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  form = ArtistForm(request.form)
  if form.validate():
    try:
      artist_name = request.form['name']
      artist_city = request.form['city']
      artist_state = request.form['state']
      artist_phone = request.form['phone']
      artist_genres = request.form.getlist('genres',type=str)
      artist_image_link = request.form['image_link']
      artist_facebook_link = request.form['facebook_link']
      artist_website_link = request.form['website_link']
      artist_seeking_venue = True if request.form['seeking_venue'] else False
      artist_seeking_description = request.form['seeking_description']
      new_artist = Artist(name=artist_name, city=artist_city, state=artist_state, phone=artist_phone, genres=artist_genres, image_link=artist_image_link, facebook_link=artist_facebook_link, website_link=artist_website_link, seeking_venue=artist_seeking_venue, seeking_description=artist_seeking_description)
      db.session.add(new_artist)
      db.session.commit()
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
      error =True
      flash('An error occurred. Artist ' + artist_name + ' could not be listed.')
      db.session.rollback()
      abort(400)
    finally:
      db.session.close()
  else:
    return render_template('forms/new_artist.html', form=form)
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.

  data=[]
  show_db = Show.query.all()
  for record in show_db:
    get_venue_db = Venue.query.get(record.venue_id)
    get_artist_db = Artist.query.get(record.artist_id)
    info = {
            "venue_id": record.venue_id,
            "venue_name": get_venue_db.name,
            "artist_id": record.artist_id,
            "artist_name": get_artist_db.name,
            "artist_image_link": get_artist_db.image_link,
            "start_time": str(record.date_time)
        }
    data.append(info)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
# called to create new shows in the db, upon submitting new show listing form
# TODO: insert form data as a new Show record in the db, instead
# on successful db insert, flash success
# TODO: on unsuccessful db insert, flash an error instead.
# e.g., flash('An error occurred. Show could not be listed.')
# see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  form = ShowForm(request.form)
  if form.validate():
    try:
      existing_artist_id = request.form['artist_id']
      existing_venue_id = request.form['venue_id']
      enter_start_time = request.form['start_time']
      new_show = Show(artist_id=existing_artist_id, venue_id=existing_venue_id, date_time=enter_start_time)
      db.session.add(new_show)
      db.session.commit()
      flash('Show was successfully listed!')
    except:
      error =True
      flash('An error occurred. Show could not be listed.')
      db.session.rollback()
    finally:
      db.session.close()
  else:
    return render_template('forms/new_show.html', form=form)
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
