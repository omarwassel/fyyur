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

from sqlalchemy.dialects.postgresql import ARRAY
import string
from datetime import datetime
from sqlalchemy import String
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__ )
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate=Migrate(app,db)

session = db.session()

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class  Shows(db.Model):
    __tablename__='Shows'
    
    venue_id=db.Column(db.Integer,db.ForeignKey('Venue.id'),primary_key=True)
    artist_id=db.Column(db.Integer,db.ForeignKey('Artist.id'),primary_key=True)
    start_time=db.Column(db.DateTime())

    # def __repr__(self):
    #         return '{ "venue_id" :{self.venue_id}, "artist_id":{self.artist_id}  }'
    


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    name_for_search = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    # genres = db.Column(db.String(120))
    genres = db.Column(ARRAY(String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    shows = db.relationship('Shows', backref='venue' , lazy=True)

    def __repr__(self):
        return '{ "id" :{self.id}, "name":{self.name} , "num_upcoming_shows" : 0 }'

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    name_for_search = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    # genres = db.Column(db.String(120))
    genres = db.Column(ARRAY(String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    shows = db.relationship('Shows', backref='artist', lazy=True)

    def __repr__(self):
        return f'<Artist {self.id} {self.genres}>'

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
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  cities=[]
  for c in db.session.query(Venue.city).distinct().all():
        cities.append(c[0])
  states=[]
  for c in db.session.query(Venue.state).distinct().all():
        states.append(c[0])
  
  data=[]
  for ct in cities:
        for st in states:
              venues=Venue.query.filter_by(city=ct).filter_by(state=st).all()
              if len(venues):
                    obj={ "city": ct, "state": st, "venues": venues}
                    data.append(obj)
        
  # print(data1)

  
  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  s='%'+request.form.get('search_term').lower()+'%'
  venues=Venue.query.filter(Venue.name_for_search.like(s))
  lst=[]
  for obj in venues:
    dic={"id":obj.id , "name":obj.name , "num_upcoming_shows":0}
    lst.append(dic) 
   
  response={
    "count": len(lst),
    "data": lst
  }
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))



@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  ch_venue=Venue.query.get(venue_id)
  # s=ch_venue.genres
  # s.replace('{', '')
  # s.replace('}', '')
  # gnrs=s.split(',')
  gnrs=ch_venue.genres
  
  past_shows = session.query(Artist).join(Shows).filter(Shows.start_time < datetime.today())\
              .filter( Shows.venue_id == venue_id ).all()
  past_lst=[]
  for a in past_shows:
    for sh in a.shows:
        if sh.start_time < datetime.today() and sh.venue_id == venue_id:
          obj={
          "artist_id": a.id,
          "artist_name": a.name,
          "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
          "start_time": str(sh.start_time)
          }
          past_lst.append(obj)
  
  
  
  coming_shows = session.query(Artist).join(Shows).filter(Shows.start_time >= datetime.today())\
                 .filter( Shows.venue_id ==  venue_id ).all()
  coming_lst=[]

  for a in coming_shows:
        for sh in a.shows:
          if sh.start_time >= datetime.today() and sh.venue_id == venue_id:
            obj={
            "artist_id": a.id,
            "artist_name": a.name,
            "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
            "start_time": str(sh.start_time)
            }
            coming_lst.append(obj)

  data={
    "id":ch_venue.id ,
    "name": ch_venue.name,
    "genres": gnrs,
    "city": ch_venue.city,
    "state": ch_venue.state,
    "phone": ch_venue.phone,
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": ch_venue.facebook_link,
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    "past_shows":past_lst,
    "upcoming_shows": coming_lst,
    "past_shows_count": len(past_lst),
    "upcoming_shows_count": len(coming_lst),
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  try:
    form = VenueForm()
    new_venue=Venue(
    name=     form.name.data,
    name_for_search=     form.name.data.lower(),
    city =    form.city.data,
    state =   form.state.data,
    address = form.address.data,
    phone =   form.phone.data,
    genres =  form.genres.data,
    facebook_link = form.facebook_link.data
  )
  # TODO: modify data to be the data object returned from db insertion
  
  # on successful db insert, flash success
    db.session.add(new_venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
  # TODO: on unsuccessful db insert, flash an error instead.
    db.session.rollback()
    flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  finally:
    db.session.close()
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
  # TODO: replace with real data returned from querying the database
  
  artist=Artist.query.all()
  data=[]
  for obj in artist:
    dic={"id":obj.id , "name":obj.name}
    data.append(dic)  

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  s='%'+request.form.get('search_term').lower()+'%'
  artists=Artist.query.filter(Artist.name_for_search.like(s)).all()
  lst=[]
  for obj in artists:
    dic={"id":obj.id , "name":obj.name , "num_upcoming_shows":0}
    lst.append(dic) 
   
  response={
    "count": len(lst),
    "data": lst
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))





@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  # print(Artist.query.get(artist_id))

  ch_artist=Artist.query.get(artist_id)

  # s=ch_artist.genres
  # s.replace('{', '')
  # s.replace('}', '')
  # gnrs=s.split(',')
  gnrs=ch_artist.genres
  print (gnrs)
  # past_shows=Shows.query.filter( Shows.start_time < datetime.today() ).filter_by( artist_id = artist_id ).all()
  # coming_shows=Shows.query.filter( Shows.start_time >= datetime.today() ).filter_by( artist_id = artist_id ).all()
 
  # past_lst=get_artist_shows(past_shows)
  # coming_lst=get_artist_shows(coming_shows)
  

  past_shows = session.query(Venue).join(Shows).filter(Shows.start_time < datetime.today())\
              .filter( Shows.artist_id == artist_id ).all()
  past_lst=[]
  for v in past_shows:
    for sh in v.shows:
        if sh.start_time < datetime.today() and sh.artist_id == artist_id:
          obj={
          "venue_id": v.id,
          "venue_name": v.name,
          "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
          "start_time": str(sh.start_time)
          }
          past_lst.append(obj)
  
  
  
  coming_shows = session.query(Venue).join(Shows).filter(Shows.start_time >= datetime.today())\
                 .filter( Shows.artist_id ==  artist_id ).all()
  coming_lst=[]

  for v in coming_shows:
        for sh in v.shows:
          if sh.start_time >= datetime.today() and sh.artist_id == artist_id:
            obj={
            "venue_id": v.id,
            "venue_name": v.name,
            "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
            "start_time": str(sh.start_time)
            }
        coming_lst.append(obj)

  data={
    "id":ch_artist.id ,
    "name": ch_artist.name,
    "genres": gnrs,
    "city": ch_artist.city,
    "state": ch_artist.state,
    "phone": ch_artist.phone,
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": ch_artist.facebook_link,
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "past_shows":past_lst,
    "upcoming_shows": coming_lst,
    "past_shows_count": len(past_lst),
    "upcoming_shows_count": len(coming_lst),
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  
  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=Artist.query.get(artist_id))

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    form = request.form
    selected_artist=Artist.query.get(artist_id)
    selected_artist.name= form['name'],
    selected_artist.genres=form['genres'],
    selected_artist.city=form['city'],
    selected_artist.state=form['state'],
    selected_artist.phone= form['phone'],
    selected_artist.facebook_link=form['facebook_link'],
    selected_artist.image_link="https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    db.session.commit()
  except:
    db.session.rollback()
    print ("erooooooooooorrrrr")
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # venue={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=Venue.query.get(venue_id))

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    form = request.form
    selected_venue=Venue.query.get(venue_id)
    selected_venue.name= form['name'],
    selected_venue.genres=form['genres'],
    selected_venue.city=form['city'],
    selected_venue.state=form['state'],
    selected_venue.phone= form['phone'],
    selected_venue.facebook_link=form['facebook_link'],
    selected_venue.image_link="https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    db.session.commit()
  except:
    db.session.rollback()
    print ("erooooooooooorrrrr")
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
  try:
    form = ArtistForm()
    new_artist=Artist(
      name=     form.name.data,
      name_for_search=     form.name.data.lower(),
      city =    form.city.data,
      state =   form.state.data,
      phone =   form.phone.data,
      genres =  form.genres.data,
      facebook_link = form.facebook_link.data
    )
  # TODO: modify data to be the data object returned from db insertion
  
  # on successful db insert, flash success
    db.session.add(new_artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
  # TODO: on unsuccessful db insert, flash an error instead.
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  shows=Shows.query.all()
  data=[]
  for sh in shows:
        obj={'venue_id':sh.venue_id,'venue_name': Venue.query.get(sh.venue_id).name,
        'artist_id':sh.artist_id,'artist_name':Artist.query.get(sh.artist_id).name ,
        "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
        "start_time": str(sh.start_time)}
        data.append(obj)
    
  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]
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
  # TODO: modify data to be the data object returned from db insertion
  try:
  # on successful db insert, flash success
    form = ShowForm()
    new_show=Shows(
    venue_id=form.venue_id.data,
    artist_id=form.artist_id.data,
    start_time= form.start_time.data
    )
    db.session.add(new_show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
  # TODO: on unsuccessful db insert, flash an error instead.
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
    
  finally:
    db.session.close()
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
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
