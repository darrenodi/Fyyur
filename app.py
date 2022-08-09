#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from datetime import datetime
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for,jsonify,abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys

#----------------------------------------------------------------------------#
# App Config.

#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database DONE
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
  # TODO: replace with real venues data. DONE
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  places = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state)
  data = []
  for area in places:

      query = Venue.query.filter(Venue.state == area.state).filter(Venue.city == area.city).all()
      print(query)
      venue_data = []

      for venue in query:
          venue_data.append({
              'id': venue.id,
              'name': venue.name,
              'num_upcoming_shows': len(db.session.query(Shows).all())
          })

          data.append({
              'city': area.city,
              'state': area.state,
              'venues': venue_data
          })

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # search for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  search = Venue.query.filter(Venue.name.contains(search_term.lower())).all()
  count = len(search)

  response={
    "count": count,
    "data": search
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = db.session.query(Venue).filter(Venue.id==venue_id).first()

  upcoming_show = Shows.query.filter(Shows.venue_id==venue_id).filter(Shows.created > datetime.now()).join(Artist,
  Shows.artist_id==Artist.id).add_columns(Artist.id,Artist.name,Artist.image_link,Shows.created).all()

  past_show = Shows.query.filter(Shows.venue_id==venue_id).filter(Shows.created < datetime.now()).join(Artist,
  Shows.artist_id==Artist.id).add_columns(Artist.id,Artist.name,Artist.image_link,Shows.created).all()

  upcoming_shows = []

  past_shows = []

  for query in upcoming_show:
    upcoming_shows.append({
      'artist_id': query[1],
      'artist_name': query[2],
      'artist_image_link': query[3],
      'created': str(query[4])
    })

  for query in past_show:
    past_shows.append({
      'artist_id': query[1],
      'artist_name': query[2],
      'artist_image_link': query[3],
      'created': str(query[4])
  })

  dataa = {
    "name": data.name,
    "id" : data.id,
    "address": data.address,
    "image_link": data.image_link,
    "city": data.city,
    "state":data.state,
    "facebook_link":data.facebook_link,
    "phone": data.phone,
    "seeking_description": data.seeking_description,
    "genres": [data.genres],
    "website_link": data.website_link,
    "seeking_talent":data.looking_for_talent,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_show),
    "upcoming_shows_count": len(upcoming_show),
  }
  return render_template('pages/show_venue.html', venue=dataa)

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
  error = False
  try:
    venue = Venue(
      name=request.form['name'],
      city=request.form['city'],
      state=request.form['state'],
      address=request.form['address'],
      phone=request.form['phone'],
      genres=request.form.getlist('genres'),
      image_link=request.form['image_link'],
      facebook_link=request.form['facebook_link'],
      website_link=request.form['website_link'],
      looking_for_talent=VenueForm(request.form).seeking_talent.data,
      seeking_description=request.form['seeking_description'])
    print("Value")
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    error = True
    flash('An error occurred. Venue ' + request.form.get("name") + ' could not be listed.')
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort(500)
  # on successful db insert, flash success
  # flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

# @app.route('/venues/<int:venue_id>/delete', methods=['DELETE'])
# def delete_venue(venue_id):
#   # TODO: Complete this endpoint for taking a venue_id, and using
#   # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
#   venue = db.session.query(Venue).filter(Venue.id==venue_id).first()
#   show = db.session.query(Shows).filter(Shows.venue_id==venue_id).all()
#   error = False
#   try:
#     db.session.delete(venue)
#     db.session.delete(show)
#     db.session.commit()
#     flash(f"Venue {venue.name} was successfully deleted.")
#   except:
#     print(sys.exc_info())
#     flash(f"An error occurred. Venue {venue.name} could not be deleted.")
#     db.session.rollback()
#     error = True
#   finally:
#     db.session.close()
#   if error:
#     abort(500)
#   # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
#   # clicking that button delete it from the db then redirect the user to the homepage
#   return render_template('pages/home.html')

@app.post('/<int:venue_id>/delete/')
def delete(venue_id):
    error = False
    venue = Venue.query.get_or_404(venue_id)
    show = db.session.query(Shows).filter(Shows.venue_id==venue_id).all()
    try:
      db.session.delete(venue)
      for shows in show:
        db.session.delete(shows)
      db.session.commit()
      flash("Delete successful")
    except:
      db.session.rollback()
      error = True
    finally:
      db.session.close()
    if error:
      abort(500)    
    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artist_query = Artist.query.all()
  return render_template('pages/artists.html', artists=artist_query)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  search = Artist.query.filter(Artist.name.contains(search_term.lower())).all()
  count = len(search)

  response={
    "count": count,
    "data": search
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  data = db.session.query(Artist).filter(Artist.id==artist_id).first()

  upcoming_show = Shows.query.filter(Shows.artist_id==artist_id).filter(Shows.created > datetime.now()).join(Venue,
  Shows.venue_id==Venue.id).add_columns(Venue.id,Venue.name,Venue.image_link,Shows.created).all()

  past_show = Shows.query.filter(Shows.artist_id==artist_id).filter(Shows.created < datetime.now()).join(Venue,
  Shows.venue_id==Venue.id).add_columns(Venue.id,Venue.name,Venue.image_link,Shows.created).all()

  upcoming_shows = []

  past_shows = []

  for query in upcoming_show:
    upcoming_shows.append({
      'venue_id': query[1],
      'venue_name': query[2],
      'venue_image_link': query[3],
      'start_time': str(query[4])
    })

  for query in past_show:
    past_shows.append({
      'venue_id': query[1],
      'venue_name': query[2],
      'venue_image_link': query[3],
      'start_time': str(query[4])
  })

  dataa = {
    "name": data.name,
    "id" : data.id,
    "image_link": data.image_link,
    "city": data.city,
    "state":data.state,
    "facebook_link":data.facebook_link,
    "phone": data.phone,
    "seeking_description": data.seeking_description,
    "genres": [data.genres],
    "website": data.website_link,
    "seeking_venue":data.looking_for_talent,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_show),
    "upcoming_shows_count": len(upcoming_show),
  }
  return render_template('pages/show_artist.html', artist=dataa)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = db.session.query(Artist).filter(Artist.id==artist_id).first()
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error=False
  try:
    artist = db.session.query(Artist).filter(Artist.id==artist_id).first()
    artist.name=request.form['name']
    artist.city=request.form['city']
    artist.state=request.form['state']
    artist.phone=request.form['phone']
    artist.genres=request.form.getlist('genres')
    artist.image_link=request.form['image_link']
    artist.facebook_link=request.form['facebook_link']
    artist.website_link=request.form['website_link']
    artist.looking_for_talent=ArtistForm(request.form).seeking_venue.data
    artist.seeking_description=request.form['seeking_description']
    db.session.commit()
  except:
      db.session.rollback()
      error = True
      print(sys.exc_info())
  finally:
      db.session.close()
  if error:
      abort(500)
  # else:
  #     return redirect(url_for('pages/home.html'))
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = db.session.query(Venue).filter(Venue.id==venue_id).first()
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error=False
  try:
    venue = db.session.query(Venue).filter(Venue.id==venue_id).first()
    venue.name=request.form['name']
    venue.city=request.form['city']
    venue.address =request.form['address']
    venue.state=request.form['state']
    venue.phone=request.form['phone']
    venue.genres=request.form.getlist('genres')
    venue.image_link=request.form['image_link']
    venue.facebook_link=request.form['facebook_link']
    venue.website_link=request.form['website_link']
    venue.looking_for_talent=VenueForm(request.form).seeking_talent.data
    venue.seeking_description=request.form['seeking_description']
    db.session.commit()
  except:
      db.session.rollback()
      error = True
      print(sys.exc_info())
  finally:
      db.session.close()
  if error:
      abort(500)
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
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
  error = False
  try:
    artist = Artist(
      name=request.form['name'],
      city=request.form['city'],
      state=request.form['state'],
      phone=request.form['phone'],
      genres=request.form.getlist('genres'),
      image_link=request.form['image_link'],
      facebook_link=request.form['facebook_link'],
      website_link=request.form['website_link'],
      looking_for_talent=ArtistForm(request.form).seeking_venue.data,
      seeking_description=request.form['seeking_description'])
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    error = True
    flash('An error occurred. Artist ' + request.form.get("name") + ' could not be listed.')
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort(500)
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  join_query = db.session.query(Shows,Venue,Artist).join(Venue,Shows.venue_id==Venue.id).join(
    Artist,Shows.artist_id==Artist.id).add_columns(Venue.id,Venue.name,Artist.id,Artist.name,Artist.image_link,Shows.created).all()
  allshows = []
  for query in join_query:
    allshows.append({
      'venue_id': query[3],
      'venue_name': query[4],
      'artist_id': query[5],
      'artist_name': query[6],
      'artist_image_link': query[7],
      'start_time': str(query[8])
    })
  return render_template('pages/shows.html', shows=allshows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  try:
    show = Shows(
      venue_id=request.form['venue_id'],
      artist_id=request.form['artist_id'],
      created=request.form['start_time'])
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    error = True
    flash('An error occurred. Show could not be listed.')
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort(500)
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
