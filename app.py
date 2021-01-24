#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime
from models import app, db, Venue, Artist, Show


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
# Migration
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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

  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

def venues():
  listallvenues=Venue.query.with_entities(Venue.id, Venue.name, Venue.city, Venue.state)
  return render_template('pages/venues.html', listallvenues=listallvenues)
  

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search= request.form.get('search_term', '')
  searchvenues = Venue.query.filter(Venue.name.ilike(f'%{search}%')).all()
  return render_template('pages/search_venues.html',searchvenues=searchvenues, search=search)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  pastshows = Show.query.filter(Show.venue_id==venue_id,Show.start_time < datetime.now()).join(Artist, Show.artist_id == Artist.id).with_entities(Artist.name,Artist.id,Artist.image_link,Show.start_time).all()
  upcomingshows = Show.query.filter(Show.venue_id==venue_id,Show.start_time > datetime.now()).join(Artist, Show.artist_id == Artist.id).with_entities(Artist.name,Artist.id,Artist.image_link,Show.start_time).all()
  return render_template('pages/show_venue.html', venue=venue, pastshows=pastshows, upcomingshows=upcomingshows)
  

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    crvenueitems = request.form
    if request.form.get('seeking_talent')=='y':
      seeking_talent=True
    else:
      seeking_talent=False
    db.session.add(Venue(
            name=crvenueitems['name'],
            city=crvenueitems['city'],
            state=crvenueitems['state'],
            address=crvenueitems['address'],
            phone=crvenueitems['phone'],
            facebook_link=crvenueitems['facebook_link'],
            image_link=crvenueitems['image_link'],
            website=crvenueitems['website'],
            seeking_talent=seeking_talent,
            seeking_description=crvenueitems['seeking_description'],
        ))
    try:
      db.session.commit()
      flash('Venue ' + crvenueitems['name'] + ' was successfully listed!')
    except:
      flash('An error occurred. Venue ' + crvenueitems['name'] + ' could not be listed.')
    finally:
      db.session.close()
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.with_entities(Artist.id, Artist.name).all()
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search= request.form.get('search_term', '')
  searchartists = Artist.query.filter(Artist.name.ilike(f'%{search}%')).all()

  return render_template('pages/search_artists.html',searchartists=searchartists, search=search)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  pastshows = Show.query.filter(Show.artist_id==artist_id,Show.start_time < datetime.now()).join(Venue, Show.venue_id == Venue.id).with_entities(Venue.name,Venue.id,Venue.image_link,Show.start_time).all()
  upcomingshows = Show.query.filter(Show.artist_id==artist_id,Show.start_time > datetime.now()).join(Venue, Show.venue_id == Venue.id).with_entities(Venue.name,Venue.id,Venue.image_link,Show.start_time).all()
  return render_template('pages/show_artist.html', artist=artist, upcomingshows=upcomingshows, pastshows=pastshows)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
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
    crartistitems = request.form
    if request.form.get('seeking_venue')=='y':
      seeking_venue=True
    else:
      seeking_venue=False
    db.session.add(Artist(
            name=crartistitems['name'],
            city=crartistitems['city'],
            state=crartistitems['state'],
            phone=crartistitems['phone'],
            genres=crartistitems['genres'],
            facebook_link=crartistitems['facebook_link'],
            image_link=crartistitems['image_link'],
            website=crartistitems['website'],
            seeking_venue=seeking_venue,
            seeking_description=crartistitems['seeking_description'],
        ))
    try:
      db.session.commit()
      flash('Venue ' + crartistitems['name'] + ' was successfully listed!')
    except:
      flash('An error occurred. Venue ' + crartistitems['name'] + ' could not be listed.')
    finally:
      db.session.close()
    return render_template('pages/home.html')
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  #checkout out the frontend
  allshows = Show.query.all()
  allartists = Artist.query.all()
  allvenues = Venue.query.all()
  return render_template('pages/shows.html', allshows=allshows, allartists=allartists, allvenues=allvenues )
@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission(): 
  crshowitems = request.form
  db.session.add(Show(
            artist_id=crshowitems['artist_id'],
            venue_id=crshowitems['venue_id'],
            start_time=crshowitems['start_time'], 
  ))
  #try:
  db.session.commit()
  flash('Show was succesfully listed!')
  #except:
   # flash('an error occured. Show could not be listed.')
  #finally:
  db.session.close()
  return render_template('pages/home.html')
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  """ flash('Show was successfully listed!') """
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  

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
