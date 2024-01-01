#libraries used
from flask_sqlalchemy import SQLAlchemy, session
from flask import Flask, redirect, url_for
from flask import render_template
from flask import request
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, relationship
from datetime import datetime
import os
import json
from flask import make_response
from flask_restful import Resource, Api, fields, marshal_with, reqparse
from werkzeug.exceptions import HTTPException
import re

#app setup
# UPLOAD_FOLDER_1 = '/static/Images'

Genres = ["Love", "Devotional", "HipHop", "Rock", "Country"]

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.sqlite3"
# app.config['UPLOAD_FOLDER_1'] = UPLOAD_FOLDER_1
app.config['IMAGES_FOLDER'] = 'static/images/'
app.config['AUDIO_FOLDER'] = 'static/audios/'
app.config['LYRICS_FOLDER'] = 'static/lyrics/'

db = SQLAlchemy()
db.init_app(app)
api = Api(app)
app.app_context().push()

engine = create_engine("sqlite:///database.sqlite3")

AdminID = "ADMIN@1034"
AdminPW = "ADMIN@1034"


#database setup
class User(db.Model):
  __tablename__ = "User"
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  UserName = db.Column(db.String(80), unique=True, nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  password = db.Column(db.String(80), nullable=False)
  ProfileImg = db.Column(db.String(80))


#table for creator
class Creator(db.Model):
  __tablename__ = "Creator"
  id = db.Column(db.Integer, db.ForeignKey("User.id"), primary_key=True)
  Bio = db.Column(db.String(120), nullable=True)
  blacklist = db.Column(db.Integer)


#table for song
class Song(db.Model):
  __tablename__ = "Song"
  Sid = db.Column(db.Integer, primary_key=True, autoincrement=True)
  SongName = db.Column(db.String(80), nullable=False)
  SongLocation = db.Column(db.String(80), nullable=False)
  Genre = db.Column(db.String(80), nullable=False)

  Cid = db.Column(db.Integer, db.ForeignKey("Creator.id"), nullable=False)
  CoverImgLoc = db.Column(db.String(80))
  NoOfStreams = db.Column(db.Integer)
  artistName = db.Column(db.String(80))
  LyricsLoc = db.Column(db.String(80))
  ReleaseDate = db.Column(db.String(15))
  album_id = db.Column(db.Integer, db.ForeignKey('Albums.Aid'))
  AvgRating = db.Column(db.Integer, default=0)


#table for playlist
class Playlist(db.Model):
  __tablename__ = "Playlist"
  Pid = db.Column(db.Integer, primary_key=True)
  PlaylistName = db.Column(db.String(80))
  Uid = db.Column(db.Integer, db.ForeignKey("User.id"))


#table for playlist and song
class songPlaylist(db.Model):
  __tablename__ = "songPlaylist"
  Pid = db.Column(db.Integer,
                  db.ForeignKey("Playlist.Pid"),
                  primary_key=True,
                  nullable=False)
  Sid = db.Column(db.Integer,
                  db.ForeignKey("Song.Sid"),
                  primary_key=True,
                  nullable=False)


#table for albums
class Albums(db.Model):
  __tablename__ = "Albums"
  Aid = db.Column(db.Integer, primary_key=True, autoincrement=True)
  AlbumName = db.Column(db.String(80), unique=True)
  Cid = db.Column(db.Integer, db.ForeignKey("Creator.id"))
  Genre = db.Column(db.String(80))
  artistName = db.Column(db.String(80))

  songs = db.relationship('Song', backref='Albums', lazy=True)


#rating
class Rating(db.Model):
  __tablename__ = "Rating"
  Uid = db.Column(db.Integer, db.ForeignKey("User.id"), primary_key=True)
  Sid = db.Column(db.Integer, db.ForeignKey("Song.Sid"), primary_key=True)
  rating = db.Column(db.Integer)


#API
#error classes for apis
#common errors
class NotFoundError(HTTPException):  #404

  def __init__(self, status_code):
    self.response = make_response('Song/Playlist not found', status_code)


class InternalServerError(HTTPException):  #500

  def __init__(self, status_code):
    self.response = make_response(status_code)


class ExistsError(HTTPException):  #409

  def __init__(self, status_code):
    self.response = make_response('Song /Playlist already exists', status_code)


class BusinessValidationError(HTTPException):  #defined errors in documentation

  def __init__(self, error_message):
    message = {"error_message": error_message}
    self.response = make_response(json.dumps(message))


#api for songs and playlists
#songs CRUD:Create read update delete
#song create
output_fields1 = {
    'Sid': fields.Integer,
    'SongName': fields.String,
    'SongLocation': fields.String,
    'Genre': fields.String,
    'Cid': fields.Integer,
    'CoverImgLoc': fields.String,
    'artistName': fields.String,
    'LyricsLoc': fields.String,
    'ReleaseDate': fields.String,
    'NoOfStreams': fields.Integer,
    'album_id': fields.Integer,
    'AvgRating': fields.Integer
}


class songAPI(Resource):

  @marshal_with(output_fields1)
  def get(self, userid, sid):
    try:
      with Session(engine) as session:
        SongPlay = session.query(Song).filter(Song.Sid == sid).first()
        if (not SongPlay):  #checking if the song exists
          raise NotFoundError(status_code=404)
          # Process the data as needed
        if (SongPlay):
          return SongPlay
    except NotFoundError as nfe:
      raise nfe
    except Exception as e:
      raise InternalServerError(status_code=500)

  def put(self, userid, sid):
    try:
      edit = False
      with Session(engine) as session:
        cr = session.query(Creator).filter(Creator.id == userid).first()
        song = session.query(Song).filter(Song.Sid == sid).first()
        if (
            not song.Cid == userid
        ):  #checking if the user trying to update is the creator of the song
          raise BusinessValidationError(
              error_message="Your not the creator of this song.")
        if ("SongName" in request.form):  #checking if song Name is given
          songName = request.form['SongName']
          songN = session.query(Song).filter(Song.SongName == songName).first()
          if (songN):  #checking if the songname is already present
            raise ExistsError(409)
          else:
            song.SongName = songName
            edit = True

        if (not song):  #checking if the song exists
          raise NotFoundError(status_code=404)
        if ('ArtistName' in request.form):
          artistName = request.form['ArtistName']
          song.artistName = artistName
          edit = True
        if ('Genre' in request.form):
          Genrei = request.form['Genre']
          if (Genrei not in Genres):
            raise BusinessValidationError(
                error_message=
                "Genre is not valid\nenter one from following:\n1.Love\n2.Love\n3.Devotional\n4.HipHop\n5.Rock\n6.Country"
            )
          song.Genre = Genrei
          edit = True
        if ('Date' in request.form):
          date = request.form['Date']
          if re.match(r'^\d{4}-\d{2}-\d{2}$', date):
            song.ReleaseDate = date
            edit = True
          else:
            raise BusinessValidationError(
                error_message="date format is incorrect use YYYY-MM-DD")
        if ('audioFile' in request.files):
          af = request.files['audioFile']
          if (not af.filename
              == ""):  #checking if audio file is changed /uploaded
            afname = str(userid) + '_' + songName + '.mp3'
            af.save(os.path.join(app.config['AUDIO_FOLDER'], afname))
            song.SongLocation = 'static/audios/' + str(afname)
            edit = True
        if ('imgFile' in request.files):
          Imgf = request.files['imgFile']
          if (not Imgf.filename
              == ""):  #checking if cover image is changed /uploaded
            imgfname = str(userid) + '_' + songName + '_cover.jpg'
            Imgf.save(os.path.join(app.config['IMAGES_FOLDER'], imgfname))
            song.CoverImgLoc = 'static/images/' + str(imgfname)
            edit = True
        if ('LyricFile' in request.files):
          lf = request.files['LyricFile']
          if (not lf.filename
              == ""):  #checking if lyric file is changed /uploaded
            lfname = str(userid) + '_' + songName + '.txt'
            lf.save(os.path.join(app.config['LYRICS_FOLDER'], lfname))
            song.LyricsLoc = 'static/lyrics/' + str(lfname)
            edit = True
        if (edit):
          session.commit()
          return {'status': 'success'}
        raise BusinessValidationError(
            error_message="enter a valid input field name")
    except BusinessValidationError as bve:
      raise bve
    except ExistsError as ee:
      raise ee
    except NotFoundError as nfe:
      raise nfe
    except Exception as e:
      raise InternalServerError(status_code=500)

  def post(self, userid):
    try:
      #get LyricFile audioFile
      with Session(engine) as session:
        cr = session.query(Creator).filter(Creator.id == userid).first()
        if (
            not cr
        ):  #checlking if the user trying to upload a song is creator or not
          raise BusinessValidationError(error_message="User is not a creator")
        if (cr.blacklist == 1):  #checking if the creator is not blacklisted
          raise BusinessValidationError(
              error_message="Creator is blacklisted can't update songs")
        if ('SongName' in request.form):
          songName = request.form['SongName']
          song = session.query(Song).filter(Song.SongName == songName).first()
          if (song):  #checking if the song name is already exists
            raise ExistsError(409)
        else:
          raise BusinessValidationError(error_message="SongName is required")
        if ('ArtistName' not in request.form):
          raise BusinessValidationError(error_message="ArtistName is required")
        if ('Genre' not in request.form):
          raise BusinessValidationError(error_message="Genre is required")
        if ('Date' not in request.form):
          raise BusinessValidationError(error_message="Date is required")
        date = request.form['Date']
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', date):
          raise BusinessValidationError(
              error_message="date format is incorrect use YYYY-MM-DD")
        if ('audioFile' not in request.files):
          raise BusinessValidationError(error_message="audioFile is required")
        if ('imgFile' not in request.files):
          raise BusinessValidationError(error_message="imgFile is required")
        if ('LyricFile' not in request.files):
          raise BusinessValidationError(error_message="LyricFile is required")

        artistName = request.form['ArtistName']
        Genres = request.form['Genre']

        af = request.files['audioFile']
        Imgf = request.files['imgFile']
        lf = request.files['LyricFile']

        print(request.form)
        afname = str(userid) + '_' + songName + '.mp3'
        print(afname)
        af.save(os.path.join(app.config['AUDIO_FOLDER'], afname))
        lfname = str(userid) + '_' + songName + '.txt'
        lf.save(os.path.join(app.config['LYRICS_FOLDER'], lfname))
        imgfname = str(userid) + '_' + songName + '_cover.jpg'
        Imgf.save(os.path.join(app.config['IMAGES_FOLDER'], imgfname))

        newSong = Song(SongName=songName,
                       SongLocation='static/audios/' + str(afname),
                       Genre=Genres,
                       Cid=userid,
                       AvgRating=0,
                       CoverImgLoc='static/images/' + str(imgfname),
                       NoOfStreams=0,
                       artistName=artistName,
                       LyricsLoc='static/lyrics/' + str(lfname),
                       ReleaseDate=date)
        session.add(newSong)
        session.commit()
        return {"status": "success"}, 200
    except BusinessValidationError as bve:
      raise bve
    except ExistsError as ee:
      raise ee
    except Exception as e:
      raise InternalServerError(status_code=500)

  def delete(self, userid, sid):
    try:
      with Session(engine) as session:
        song = session.query(Song).filter(Song.Sid == sid).first()
        if (not song.Cid
            == userid):  #checking if the user is  the creator of song
          raise BusinessValidationError(
              error_message="Your not the creator of this song.")
        if (not song):  #checking if the songName exists
          raise NotFoundError(404)
        songLoc = song.SongLocation
        songCoverImg = song.CoverImgLoc
        songLyrics = song.LyricsLoc
        os.remove(songLoc)
        os.remove(songCoverImg)
        os.remove(songLyrics)
        print("File deleted successfully.")
        session.delete(song)
        session.commit()
        return {"status": "success"}, 200
    except BusinessValidationError as bve:
      raise bve
    except NotFoundError as nfe:
      raise nfe
    except Exception as e:
      raise InternalServerError(status_code=500)


api.add_resource(songAPI, "/api/user/<int:userid>/song/<int:sid>",
                 "/api/user/<int:userid>/song")

output_fields2 = {
    'Pid': fields.Integer,
    'PlaylistName': fields.String,
    'Uid': fields.Integer
}


#playlist api
class playListAPI(Resource):

  @marshal_with({
      'playlist': fields.Nested(output_fields2),
      'songs': fields.List(fields.Nested(output_fields1))
  })
  def get(self, Userid, Pid):
    try:
      with Session(engine) as session:
        Playlists = session.query(Playlist).filter(
            Playlist.Pid == Pid, Playlist.Uid == Userid).first()
        if (not Playlists):
          raise NotFoundError(status_code=404)
        songPlaylists = session.query(songPlaylist).filter(
            songPlaylist.Pid == Pid).all()
        Playlists = session.query(Playlist).filter(Playlist.Pid == Pid).first()
        print(songPlaylists)
        songs = []
        for i in songPlaylists:
          songs.append(session.query(Song).filter(Song.Sid == i.Sid).first())
          print(songs)
        return {'playlist': Playlists, 'songs': songs}
    except NotFoundError as nfe:
      raise nfe
    except Exception as e:
      raise e

  def post(self, Userid):
    try:
      if ('PlaylistName' not in request.form):
        raise BusinessValidationError(
            error_message="PlaylistName is requeried")
      if ('Checkedsongs' not in request.form):
        raise BusinessValidationError(error_message="CheckedSongs is required")
      PlaylistName = request.form['PlaylistName']
      Checkedsongs = request.form.getlist('Checkedsongs')
      with Session(engine) as session:
        pl = session.query(Playlist).filter(
            Playlist.PlaylistName == PlaylistName).first()
        if (pl):
          raise ExistsError(status_code=409)
        newPlaylist = Playlist(PlaylistName=PlaylistName, Uid=Userid)
        session.add(newPlaylist)
        session.commit()
      with Session(engine) as session:
        newPlaylist = session.query(Playlist).filter(
            Playlist.Uid == Userid).order_by(Playlist.Pid.desc()).first()
        print(newPlaylist)
        for i in Checkedsongs:
          newsongPlaylist = songPlaylist(Pid=newPlaylist.Pid, Sid=i)

          session.add(newsongPlaylist)
        session.commit()
      return {"status": "success"}, 200
    except ExistsError as ee:
      raise ExistsError(status_code=409)
    except Exception as e:
      raise InternalServerError(status_code=500)

  def put(self, Userid, Pid):
    try:

      edit = False

      with Session(engine) as session:
        #check if the user is the creator of that playlist
        sids = []
        PlaylistIn = session.query(songPlaylist.Sid).filter(
            songPlaylist.Pid == Pid).all()  #contains PID and Sid
        # contains sids of songs in playlist
        for i in PlaylistIn:
          for j in i:
            sids.append(j)
        songOwn = session.query(Playlist).filter(
            Playlist.Pid == Pid, Playlist.Uid == Userid).first()
        if (not songOwn.Uid == Userid):
          raise BusinessValidationError(
              error_message="user id is the creator of this playlist")
        if ('PlaylistName'
            in request.form):  #checking if user is updating the playlist name
          PlaylistName = request.form['PlaylistName']
          pl = session.query(Playlist).filter(
              Playlist.PlaylistName == PlaylistName).first()
          if (pl):  #checking for duplication of playlist name
            raise ExistsError(status_code=409)
          editPlaylist = session.query(Playlist).filter(
              Playlist.Pid == Pid, Playlist.Uid == Userid).first()
          if (not editPlaylist):
            raise NotFoundError(status_code=404)
          editPlaylist.PlaylistName = PlaylistName  #playlist name set
          edit = True
        if ('Addsongs' in request.form):
          Addsongs = request.form.getlist('Addsongs')
          #add songs to playlist

          newSids = []
          print("sids already present", sids)
          checked = []
          for i in Addsongs:
            checked.append(int(i))
          for i in checked:
            if (i not in sids):  # if song not present in playlist
              #add new song to playlist
              newSids.append(int(i))
              newsongPlaylist = songPlaylist(Pid=Pid, Sid=int(i))
              session.add(newsongPlaylist)
          print("new sids added", newSids)
          edit = True
        if ('RemoveSongs' in request.form):
          RemoveSongs = request.form.getlist('RemoveSongs')
          print(RemoveSongs)
          print(sids)
          # remove songs from playlist
          for i in sids:
            print(str(i) in RemoveSongs)
            print(str(i))
            if (str(i) in RemoveSongs):
              print(i)
              #remove song from playlist
              songdel = session.query(songPlaylist).filter(
                  songPlaylist.Pid == Pid, songPlaylist.Sid == i).first()
              if (not songdel):
                raise BusinessValidationError(
                    error_message="Song : is not present in the playlist")
              print("song that will be deleted:", songdel)
              session.delete(songdel)
          edit = True

        if (edit):
          print("Done")
          session.commit()
          return {"status": "success"}, 200
        else:
          print("Not done")
          raise BusinessValidationError(error_message="Form body is missing")
    except BusinessValidationError as bve:
      raise bve
    except ExistsError as ee:
      raise ExistsError(status_code=409)
    except NotFoundError as nfe:
      raise nfe
    except Exception as e:
      raise InternalServerError(status_code=500)

  def delete(self, Userid, Pid):
    try:
      with Session(engine) as session:
        songPlaylists = session.query(songPlaylist).filter(
            songPlaylist.Pid == Pid).all()
        playlist = session.query(Playlist).filter(
            Playlist.Pid == Pid, Playlist.Uid == Userid).all()
        if (not playlist):
          raise NotFoundError(status_code=404)
        for i in songPlaylists:
          session.delete(i)
        for i in playlist:
          session.delete(i)
        session.commit()
      return {"status": "success"}, 200
    except NotFoundError as nfe:
      raise nfe
    except Exception as e:
      raise InternalServerError(status_code=500)


api.add_resource(playListAPI, "/api/user/<int:Userid>/playlist/<int:Pid>",
                 "/api/user/<int:Userid>/playlist")

# app routes


#login page
@app.route('/', methods=["GET", "POST"])
def UserLogin():
  if (request.method == "GET"):  #rendering login page
    with Session(engine) as session:
      usersInfo = session.query(User.UserName, User.password).all()
      print(usersInfo)
    return render_template("login.html", wrong=False)
  elif (request.method == "POST"):
    userName = request.form["UserName"]
    password = request.form["Password"]
    #check if the username is in db
    with Session(engine) as session:
      user = session.query(User).filter((User.UserName == userName)
                                        & (User.password == password)).first()
      if (not user):
        return render_template("login.html", wrong=True)
      else:
        print(user.password, password)
        return redirect(url_for("Home", userid=user.id))

    #if true check if pw is correct
    #then render his home page
    #else render login page again with user not found in red


#sign up page
@app.route("/UserRegistration", methods=["GET", "POST"])
def UserRegistration():
  print("InUserREg")
  if (request.method == "GET"):  #rendering login page
    print("InUserREget")
    return render_template("Registration.html", error=False)
  elif (request.method == "POST"):  # elif(request.method=="POST"):
    print("InuserRegPost")
    userName = request.form["Name"]
    password = request.form["password"]
    email = request.form["email"]
    print(userName, password)
    #check if the username is in db
    with Session(engine) as session:
      user = session.query(User).filter(User.UserName == userName).all()
      if (user):
        return render_template("Registration.html", error1=True)
      user = session.query(User).filter(User.email == email).all()
      if (user):
        return render_template("Registration.html", error2=True)
      else:
        #add user to db
        newUser = User(UserName=userName, password=password, email=email)
        session.add(newUser)
        print(newUser)
        session.commit()
        return render_template("login.html")


#home page
@app.route("/Home/<int:userid>", methods=["GET"])
def Home(userid):
  with Session(engine) as session:
    Users = session.query(User).filter(User.id == userid).first()
    playlists = session.query(Playlist).filter(Playlist.Uid == userid).all()
    albums = session.query(Albums).all()
    print(playlists)
    songs = session.query(Song).order_by(Song.AvgRating.desc()).all()

    k = 0
    courselSetSong = [songs[i:i + 4] for i in range(0, len(songs), 4)]
    courselSetalbums = [albums[i:i + 4] for i in range(0, len(albums), 4)]
    courselSetplaylist = [
        playlists[i:i + 4] for i in range(0, len(playlists), 4)
    ]

    songsData = [{
        'songName': song.SongName,
        'artistName': song.artistName,
        'Sid': song.Sid,
        'Genre': song.Genre,
        'CoverImgLoc': song.CoverImgLoc,
        'AvgRating': song.AvgRating,
        'NoOfStreams': song.NoOfStreams
    } for song in songs]

    GenreData = [{'Genre': genre} for genre in Genres]

    albumsData = [{
        'AlbumName': album.AlbumName,
        'Cid': album.Cid,
        'Aid': album.Aid,
        'artist': album.artistName,
        'Genrei': album.Genre
    } for album in albums]

    playlistData = [{
        'PlaylistName': playlist.PlaylistName,
        'Uid': playlist.Uid,
        'Pid': playlist.Pid
    } for playlist in playlists]

    print(courselSetplaylist)
    GenreSet = [Genres[i:i + 4] for i in range(0, len(Genres), 4)]
    return render_template("Home.html",
                           Userid=userid,
                           GenreData=GenreData,
                           songsData=songsData,
                           albumsData=albumsData,
                           playlistData=playlistData,
                           Genre=GenreSet,
                           song=courselSetSong,
                           albums=courselSetalbums,
                           courselSetplaylist=courselSetplaylist)


#profile page
@app.route("/Profile/<int:userid>", methods=["GET"])
def Profile(userid):
  if (request.method == "GET"):
    with Session(engine) as session:
      Users = session.query(User).filter(User.id == userid).first()
      Profile = bool(Users.ProfileImg)
      return render_template("userProfile.html",
                             Users=Users,
                             edit=False,
                             profile=Profile)


#profile edit
@app.route("/Profile/<int:userid>/edit", methods=["GET", "POST"])
def userEdit(userid):
  if (request.method == "GET"):
    with Session(engine) as session:
      users = session.query(User).filter(User.id == userid).first()
      Profile = bool(users.ProfileImg)
      return (render_template("userProfile.html",
                              Users=users,
                              edit=True,
                              profile=Profile))
  if (request.method == "POST"):
    Name = request.form["Name"]
    email = request.form["email"]
    with Session(engine) as session:
      users = session.query(User).filter(User.id == userid).first()
      profile = bool(users.ProfileImg)
      users.UserName = Name
      users.email = email
      if ('ProfileImg' in request.files):
        f = request.files['ProfileImg']
        if (not f.filename == ""):
          filename = str(userid) + "Profile.jpg"
          # Save the file to the upload folder
          f.save(os.path.join(app.config['IMAGES_FOLDER'], filename))
          profile = True
          users.ProfileImg = app.config['IMAGES_FOLDER'] + filename

      session.commit()
      return render_template("userProfile.html",
                             Users=users,
                             edit=False,
                             profile=profile)


#view Genre
@app.route("/viewGenre/<int:userid>/<string:genre>")
def viewGenre(userid, genre):
  with Session(engine) as session:
    songs = session.query(Song).filter(Song.Genre == genre).all()
    return render_template("viewGenre.html",
                           songs=songs,
                           genre=genre,
                           userid=userid)


#creator routes


#creator dashboard
@app.route("/Creator/<int:userId>", methods=["GET"])
def CreatorHandler(userId, edit=False):
  with Session(engine) as session:
    if (request.method == "GET"):
      Creators = session.query(Creator).filter(Creator.id == userId).first()
      if (Creators):
        user = session.query(User).filter(User.id == userId).first()
        Songs = session.query(Song).filter(Song.Cid == userId).all()
        MostRatedSongs = session.query(Song).order_by(
            Song.AvgRating.desc()).filter(Song.Cid == userId).limit(5).all()
        MostStreamedSongs = session.query(Song).order_by(
            Song.NoOfStreams.desc()).filter(Song.Cid == userId).limit(5).all()

        albums = session.query(Albums).filter(Albums.Cid == userId).all()
        Scount, Acount, SumRating = 0, 0, 0
        for i in Songs:
          Scount += 1
          SumRating += i.AvgRating
        for i in albums:
          Acount += 1
        MSNoArr, MSSongNamesArr = [], []
        for i in MostStreamedSongs:
          MSNoArr.append(i.NoOfStreams)
          MSSongNamesArr.append(i.SongName)
        MRNoArr, MRSongNamesArr = [], []
        for i in MostRatedSongs:
          MRNoArr.append(i.AvgRating)
          MRSongNamesArr.append(i.SongName)
        chartData1 = {
            "MSSongNamesArr": MSSongNamesArr,
            "MSNoArr": MSNoArr,
            "MAXy": max(MSNoArr) if (len(MSNoArr) > 0) else 0
        }
        chartData2 = {
            "MRSongNamesArr": MRSongNamesArr,
            "MRNoArr": MRNoArr,
            "MAXy": max(MRNoArr) if (len(MSNoArr) > 0) else 0
        }
        #update count of songs
        #update rating
        #need to send songs of creator
        Profile = bool(user.ProfileImg)
        return render_template("CreatorDashboard.html",
                               edit=edit,
                               Creator=Creators,
                               user=user,
                               profile=Profile,
                               Songs=Songs,
                               Scount=Scount,
                               Acount=Acount,
                               albums=albums,
                               chartData1=chartData1,
                               chartData2=chartData2,
                               AvgRating=(SumRating /
                                          Scount) if not Scount == 0 else 0)
      else:
        return render_template("SwitchToCreator.html", userId=userId)


#edit Bio
@app.route("/Creator/<int:userId>/edit", methods=["GET", "POST"])
def editCreatorDashboard(userId):
  with Session(engine) as session:
    if (request.method == "GET"):
      Creators = session.query(Creator).filter(Creator.id == userId).all()
      if (Creators):
        user = session.query(User).filter(User.id == userId).first()
        Songs = session.query(Song).filter(Song.Cid == userId).all()
        MostStreamedSongs = session.query(Song).order_by(
            Song.NoOfStreams.desc()).filter(Song.Cid == userId).limit(5).all()
        MostRatedSongs = session.query(Song).order_by(
            Song.AvgRating.desc()).filter(Song.Cid == userId).limit(5).all()
        albums = session.query(Albums).filter(Albums.Cid == userId).all()
        Scount, Acount, SumRating = 0, 0, 0
        for i in Songs:
          Scount += 1
          SumRating += i.AvgRating
        for i in albums:
          Acount += 1
        MSNoArr, MSSongNamesArr = [], []
        for i in MostStreamedSongs:
          MSNoArr.append(i.NoOfStreams)
          MSSongNamesArr.append(i.SongName)
        MRNoArr, MRSongNamesArr = [], []
        for i in MostRatedSongs:
          MRNoArr.append(i.AvgRating)
          MRSongNamesArr.append(i.SongName)
        chartData1 = {
            "MSSongNamesArr": MSSongNamesArr,
            "MSNoArr": MSNoArr,
            "MAXy": max(MSNoArr) if (len(MSNoArr) > 0) else 0
        }
        chartData2 = {
            "MRSongNamesArr": MRSongNamesArr,
            "MRNoArr": MRNoArr,
            "MAXy": max(MRNoArr) if (len(MSNoArr) > 0) else 0
        }
        #update count of songs
        #update rating
        #need to send songs of creator
        Profile = bool(user.ProfileImg)
        return render_template("CreatorDashboard.html",
                               edit=True,
                               Creator=Creators,
                               user=user,
                               profile=Profile,
                               Songs=Songs,
                               Scount=Scount,
                               Acount=Acount,
                               albums=albums,
                               chartData1=chartData1,
                               chartData2=chartData2,
                               AvgRating=(SumRating /
                                          Scount) if not Scount == 0 else 0)
      else:
        return render_template("SwitchToCreator.html", userId=userId)
    elif (request.method == "POST"):

      Creators = session.query(Creator).filter(Creator.id == userId).first()

      if not request.form["bio"] == "":
        Creators.Bio = request.form["bio"]
        session.commit()
      return redirect(url_for("CreatorHandler", userId=userId))


#add user as creator
@app.route("/Creator/<int:userId>/addCreator")
def AddCreator(userId):
  if (request.method == "GET"):
    with Session(engine) as session:
      newCreator = Creator(id=userId, Bio="", blacklist=0)
      session.add(newCreator)
      session.commit()
      user = session.query(User).filter(User.id == userId).all()
      Creators = session.query(Creator).filter(Creator.id == userId).all()
      return redirect(url_for("CreatorHandler", userId=userId))


#rating songs
@app.route("/Song/<int:Sid>/<int:userid>/Song/rate/<string:rate>",
           methods=["GET"])
def rateSong(userid, Sid, rate):
  rating = int(rate)  #changing string to int for cal
  print("rating:", rating)
  if (request.method == "GET"):
    print("in rating")
    with Session(engine) as session:
      ratings = session.query(Rating).filter(
          Rating.Sid == Sid,
          Rating.Uid == userid).first()  #getting prev rating of the user

      NoOfRatings = session.query(Rating).filter(
          Rating.Sid == Sid).count()  #getting the no of rating that song have
      song = session.query(Song).filter(
          Song.Sid == Sid).first()  #getting song for updating avg rating
      if ratings is None:  #if the user doesn't rated this song till now
        print("new rating")
        newratings = Rating(Sid=Sid, Uid=userid, rating=rate)
        session.add(newratings)  #adding the rating to rating table
        print("multi:", (song.AvgRating * NoOfRatings))
        # print("sub", (ratings.rating))
        print("add", rating)
        print("no", NoOfRatings)
        print(
            "result",
            round(
                ((song.AvgRating * NoOfRatings) + rating) / (NoOfRatings + 1),
                2))
        if NoOfRatings != 0:  # if the song isnt rated by any user
          song.AvgRating = round(
              ((song.AvgRating * NoOfRatings) + rating) / (NoOfRatings + 1), 2)
        else:
          song.AvgRating = round(rating, 2)
        song.NoOfStreams -= 1
        print("new:", song.AvgRating)
        session.commit()
      else:
        print("update rating")

        print("prev", song.AvgRating)
        if NoOfRatings != 0:
          ratingSum = song.AvgRating * NoOfRatings
          print(ratingSum)
          actualSum = ratingSum + rating - ratings.rating
          print(actualSum)
          print("no", NoOfRatings)
          song.AvgRating = round((actualSum) / (NoOfRatings), 2)
        ratings.rating = rating
        print("Updated", song.AvgRating)

        song.NoOfStreams -= 1
        session.commit()
      return redirect(url_for("play", userid=userid, Sid=Sid))


#create albums
@app.route("/Creator/<int:userid>/CreateAlbum", methods=["POST", "GET"])
def createAlbum(userid):
  if (request.method == "GET"):
    with Session(engine) as session:
      songs = session.query(Song).filter(Song.Cid == userid,
                                         Song.album_id == 0).all()
      print(songs)
      return render_template("CreateAlbum.html",
                             userid=userid,
                             songs=songs,
                             error=False)
  if (request.method == "POST"):

    with Session(engine) as session:
      AlbumName = request.form['AlbumName']
      # dupAl = session.query(Albums).filter(Albums.AlbumName == AlbumName).first()
      # if dupAl:
      #   songs = session.query(Song).filter(Song.Cid == userid,
      #                                      Song.album_id == 0).all()
      #   return render_template("CreateAlbum.html",
      #                          userid=userid,
      #                          songs=songs,
      #                          error=True)
      artistName = request.form['artistName']
      GenreI = request.form['Genre']
      print(artistName, GenreI)
      Checkedsongs = request.form.getlist('Checkedsongs')

      newAlbum = Albums(AlbumName=AlbumName,
                        Genre=GenreI,
                        artistName=artistName,
                        Cid=userid)
      session.add(newAlbum)
      for i in range(len(Checkedsongs)):
        song = session.query(Song).filter(Song.Sid == Checkedsongs[i]).first()
        song.album_id = newAlbum.Aid

      session.commit()
      return redirect(url_for("CreatorHandler", userId=userid))


#view Album
@app.route("/<int:userid>/Album/<int:Aid>/View")
def viewAlbum(userid, Aid):
  if (request.method == "GET"):
    with Session(engine) as session:
      Songs = session.query(Song).filter(Song.album_id == Aid).all()
      albums = session.query(Albums).filter(Albums.Aid == Aid).first()
      return render_template("viewAlbum.html",
                             userid=userid,
                             songs=Songs,
                             album=albums)


#edit album
@app.route("/Creator/<int:userid>/Album/<int:Aid>/edit",
           methods=["GET", "POST"])
def editAlbum(userid, Aid):
  if (request.method == "GET"):
    with Session(engine) as session:
      songs = session.query(Song).filter(Song.Cid == userid).all()
      albums = session.query(Albums).filter(Albums.Aid == Aid).first()
      return render_template("editAlbum.html",
                             userid=userid,
                             songs=songs,
                             albums=albums,
                             error=False)
  if (request.method == "POST"):

    with Session(engine) as session:
      AlbumName = request.form['AlbumName']
      artistName = request.form['artistName']
      GenreI = request.form['Genre']
      Checkedsongs = request.form.getlist('Checkedsongs')
      dupAl = session.query(Albums).filter(Albums.AlbumName == AlbumName,
                                           Albums.Aid != Aid).first()
      if dupAl:
        songs = session.query(Song).filter(Song.Cid == userid).all()
        albums = session.query(Albums).filter(Albums.Aid == Aid).first()
        return render_template("editAlbum.html",
                               userid=userid,
                               songs=songs,
                               albums=albums,
                               error=True)
      albums = session.query(Albums).filter(Albums.Aid == Aid).first()
      albums.AlbumName = AlbumName
      albums.artistName = artistName
      albums.Genre = GenreI
      albums.songs = []
      for i in range(len(Checkedsongs)):
        song = session.query(Song).filter(Song.Sid == Checkedsongs[i]).first()
        albums.songs.append(song)
      session.commit()
      return redirect(url_for("CreatorHandler", userId=userid))


#delete album
@app.route("/Creator/<int:userid>/Album/<int:Aid>/delete")
def deleteAlbum(userid, Aid):
  with Session(engine) as session:
    album = session.query(Albums).filter(Albums.Aid == Aid).first()
    print(album)
    songs = session.query(Song).filter(Song.album_id == Aid).all()
    for i in range(len(songs)):
      songs[i].album_id = 0

    session.delete(album)
    session.commit()
    return (redirect(url_for("CreatorHandler", userId=userid)))


#playlist creation
@app.route("/Home/<int:userid>/createPlaylist", methods=["GET", "POST"])
def CreatePlaylist(userid):
  if (request.method == "GET"):
    with Session(engine) as session:
      Songs = session.query(Song).all()
      return render_template("createPlaylist.html",
                             userid=userid,
                             Songs=Songs,
                             error=False)
  if (request.method == "POST"):
    PlaylistName = request.form['PlaylistName']
    Checkedsongs = request.form.getlist('Checkedsongs')
    with Session(engine) as session:
      duplPly = session.query(Playlist).filter(
          Playlist.PlaylistName == PlaylistName,
          Playlist.Uid == userid).first()
      if (duplPly):
        Songs = session.query(Song).all()
        return render_template("createPlaylist.html",
                               userid=userid,
                               Songs=Songs,
                               error=True)
      newPlaylist = Playlist(PlaylistName=PlaylistName, Uid=userid)
      session.add(newPlaylist)
      session.commit()
    with Session(engine) as session:
      newPlaylist = session.query(Playlist).filter(
          Playlist.Uid == userid).order_by(Playlist.Pid.desc()).first()
      print(newPlaylist)
      for i in Checkedsongs:
        newsongPlaylist = songPlaylist(Pid=newPlaylist.Pid, Sid=i)
        session.add(newsongPlaylist)
      session.commit()
    return redirect(url_for("Home", userid=userid))


#view playlist
@app.route("/Home/<int:Userid>/playlist/<int:Pid>")
def viewPlaylist(Userid, Pid):
  if (request.method == "GET"):
    with Session(engine) as session:
      songPlaylists = session.query(songPlaylist).filter(
          songPlaylist.Pid == Pid).all()
      Playlists = session.query(Playlist).filter(Playlist.Pid == Pid).first()
      print(songPlaylists)
      songs = []
      for i in songPlaylists:
        songs.append(session.query(Song).filter(Song.Sid == i.Sid).first())
        print(songs)
      return render_template("viewPlaylist.html",
                             Userid=Userid,
                             songs=songs,
                             Playlists=Playlists)


#edit playlist
@app.route("/Home/<int:Userid>/playlist/<int:Pid>/Edit",
           methods=["GET", "POST"])
def editPlaylist(Userid, Pid):
  if (request.method == "GET"):
    with Session(engine) as session:
      songPlaylists = session.query(songPlaylist).filter(
          songPlaylist.Pid == Pid).all()
      Playlists = session.query(Playlist).filter(Playlist.Pid == Pid).first()
      print(songPlaylists)
      songsChecked = []
      for i in songPlaylists:
        songsChecked.append(
            session.query(Song).filter(Song.Sid == i.Sid).first())
        print(songsChecked)
      song = session.query(Song).all()
      return render_template("editPlaylist.html",
                             Userid=Userid,
                             songsChecked=songsChecked,
                             songs=song,
                             Playlists=Playlists)
  if (request.method == "POST"):
    PlaylistName = request.form['PlaylistName']
    Checkedsongs = request.form.getlist('Checkedsongs')
    with Session(engine) as session:
      editPlaylist = session.query(Playlist).filter(
          Playlist.Pid == Pid).first()
      editPlaylist.PlaylistName = PlaylistName  #playlist name set
      #add songs to playlist
      PlaylistIn = session.query(songPlaylist.Sid).filter(
          songPlaylist.Pid == Pid).all()  #contains PID and Sid
      sids = []  # contains sids of songs in playlist
      for i in PlaylistIn:
        for j in i:
          sids.append(j)
      newSids = []
      print("sids already present", sids)
      checked = []
      for i in Checkedsongs:
        checked.append(int(i))
      for i in checked:
        if (i not in sids):
          #add new song to playlist
          newSids.append(int(i))
          newsongPlaylist = songPlaylist(Pid=Pid, Sid=int(i))
          session.add(newsongPlaylist)
      print("new sids added", newSids)
      # remove songs from playlist that are  checked before but not now
      for i in sids:
        print(i)
        if (i not in checked):
          #remove song from playlist
          songdel = session.query(songPlaylist).filter(
              songPlaylist.Pid == Pid, songPlaylist.Sid == i).first()
          session.delete(songdel)
      session.commit()
    return redirect(url_for("Home", userid=Userid))


#delete playlist
@app.route("/Home/<int:Userid>/playlist/<int:Pid>/delete")
def deletePlaylist(Userid, Pid):
  with Session(engine) as session:
    songPlaylists = session.query(songPlaylist).filter(
        songPlaylist.Pid == Pid).all()
    playlist = session.query(Playlist).filter(Playlist.Pid == Pid,
                                              Playlist.Uid == Userid).all()
    for i in songPlaylists:
      session.delete(i)
    for i in playlist:
      session.delete(i)
    session.commit()
    return (redirect(url_for("Home", userid=Userid)))


#Song routes
#upload Song
@app.route('/Creator/<int:userid>/UploadSong', methods=["GET", "POST"])
def uploadSong(userid):
  if (request.method == "GET"):
    return render_template("UploadSong.html", userid=userid, exists=False)
  if (request.method == "POST"):
    songName = request.form['SongName']

    artistName = request.form['ArtistName']
    Genrei = request.form['Genre']
    date = request.form['Date']
    #get LyricFile audioFile
    with Session(engine) as session:
      songDup = session.query(Song).filter(Song.SongName == songName).first()
      if (songDup):
        return render_template("UploadSong.html", userid=userid, exists=True)
      af = request.files['audioFile']
      Imgf = request.files['imgFile']
      lf = request.files['LyricFile']
      afname = str(userid) + '_' + songName + '.mp3'
      print(afname)
      af.save(os.path.join(app.config['AUDIO_FOLDER'], afname))
      lfname = str(userid) + '_' + songName + '.txt'
      lf.save(os.path.join(app.config['LYRICS_FOLDER'], lfname))
      imgfname = str(userid) + '_' + songName + '_cover.jpg'
      Imgf.save(os.path.join(app.config['IMAGES_FOLDER'], imgfname))
      date_obj = datetime.strptime(date, '%Y-%m-%d')
      date_string = date_obj.strftime('%Y-%m-%d')
      print(date_string)
      newSong = Song(SongName=songName,
                     SongLocation='static/audios/' + str(afname),
                     Genre=Genrei,
                     Cid=userid,
                     AvgRating=0,
                     CoverImgLoc='static/images/' + str(imgfname),
                     NoOfStreams=0,
                     artistName=artistName,
                     LyricsLoc='static/lyrics/' + str(lfname),
                     ReleaseDate=date_string,
                     album_id=0)
      session.add(newSong)
      session.commit()
    print("song saved")
    return redirect(url_for("CreatorHandler", userId=userid))


#play song
@app.route("/Song/<int:userid>/<int:Sid>/play")
def play(userid, Sid):
  with Session(engine) as session:
    SongPlay = session.query(Song).filter(Song.Sid == Sid).first()
    cr = session.query(Creator).filter(Creator.id == SongPlay.Cid).first()
    crDetails = session.query(User).filter(User.id == cr.id).first()
    SongPlay.NoOfStreams += 1
    Lyrics = ""
    with open(SongPlay.LyricsLoc, 'r') as file:
      Lyrics = file.read()
      # Process the data as needed
    user = session.query(User.id).filter(User.id == SongPlay.Cid).first()
    session.commit()
    return render_template("SongStream.html",
                           Song=SongPlay,
                           Lyrics=Lyrics,
                           userid=userid,
                           cr=cr,
                           crDetails=crDetails)


#delete song
@app.route("/<int:userid>/Song/<int:Sid>/delete")
def deleteSong(userid, Sid):
  with Session(engine) as session:
    song = session.query(Song).filter(Song.Sid == Sid).first()
    playlists = session.query(songPlaylist).filter(
        songPlaylist.Sid == Sid).all()
    for i in playlists:  #remove songs from playlists
      session.delete(i)
    songRatings = session.query(Rating).filter(
        Rating.Sid == Sid).all()  #remove rating
    for i in songRatings:
      session.delete(i)
    songLoc = song.SongLocation
    songCoverImg = song.CoverImgLoc
    songLyrics = song.LyricsLoc
    os.remove(songLoc)
    os.remove(songCoverImg)
    os.remove(songLyrics)
    print("File deleted successfully.")
    session.delete(song)
    session.commit()
  #if creator go to creator dashboard
  return redirect(url_for("CreatorHandler", userId=userid))


#song edit
@app.route("/Creator/<int:userid>/Song/<int:Sid>/edit",
           methods=["POST", "GET"])
def editSong(userid, Sid):
  if (request.method == "GET"):
    with Session(engine) as session:
      song = session.query(Song).filter(Song.Sid == Sid).first()
      return render_template("SongEdit.html", song=song, userid=userid)
  if (request.method == "POST"):

    #get LyricFile audioFile
    with Session(engine) as session:
      songName = request.form['SongName']
      song = session.query(Song).filter(Song.Sid == Sid).first()
      songDup = session.query(Song).filter(Song.SongName == songName,
                                           Song.Sid != Sid).first()
      if (songDup):
        return render_template("SongEdit.html",
                               userid=userid,
                               song=song,
                               exists=True)
      artistName = request.form['ArtistName']
      Genrei = request.form['Genre']
      date = request.form['Date']

      af = request.files['audioFile']
      Imgf = request.files['imgFile']
      lf = request.files['LyricFile']
      song = session.query(Song).filter(Song.Sid == Sid).first()
      if (not af.filename == ""):
        afname = str(userid) + '_' + songName + '.mp3'
        af.save(os.path.join(app.config['AUDIO_FOLDER'], afname))
        song.SongLocation = 'static/audios/' + str(afname)
      if (not lf.filename == ""):
        lfname = str(userid) + '_' + songName + '.txt'
        lf.save(os.path.join(app.config['LYRICS_FOLDER'], lfname))
        song.LyricsLoc = 'static/lyrics/' + str(lfname)
      if (not Imgf.filename == ""):
        imgfname = str(userid) + '_' + songName + '_cover.jpg'
        Imgf.save(os.path.join(app.config['IMAGES_FOLDER'], imgfname))
        song.CoverImgLoc = 'static/images/' + str(imgfname)
      if (date):
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        date_string = date_obj.strftime('%Y-%m-%d')
        print(date_string)
      song.SongName = songName
      song.Genre = Genrei
      song.artistName = artistName
      song.ReleaseDate = date_string
      session.commit()
      return redirect(url_for("CreatorHandler", userId=userid))


#adminlogin
@app.route('/adminLogin', methods=["GET", "POST"])
def AdminLogin():
  if (request.method == "GET"):  #rendering login page
    return render_template("AdminLogin.html", wrong=False)
  elif (request.method == "POST"):
    adminUS = request.form['username']
    adminpw = request.form['password']
    if (adminpw == AdminPW and adminUS == AdminID):
      return redirect(url_for("AdminHandler"))
    return render_template("AdminLogin.html", wrong=True)

  #check if the username is in db
  #if true check if pw is correct
  #then render his home page
  #else render login page again with user not found in red


#admin dashbooard
@app.route('/Admin/Dashboard')
def AdminHandler():
  with Session(engine) as session:
    users = session.query(User).count()
    Creators = session.query(Creator).count()
    Songs = session.query(Song).all()
    albums = session.query(Albums).count()
    MostRatedSongs = session.query(Song).order_by(
        Song.AvgRating.desc()).limit(5).all()
    MostStreamedSongs = session.query(Song).order_by(
        Song.NoOfStreams.desc()).limit(5).all()

    Scount, SumRating = 0, 0
    for i in Songs:
      Scount += 1
      SumRating += i.AvgRating

    MSNoArr, MSSongNamesArr = [], []
    for i in MostStreamedSongs:
      MSNoArr.append(i.NoOfStreams)
      MSSongNamesArr.append(i.SongName)
    MRNoArr, MRSongNamesArr = [], []
    for i in MostRatedSongs:
      MRNoArr.append(i.AvgRating)
      MRSongNamesArr.append(i.SongName)
    chartData1 = {
        "MSSongNamesArr": MSSongNamesArr,
        "MSNoArr": MSNoArr,
        "MAXy": max(MSNoArr) if (len(MSNoArr) > 0) else 0
    }
    chartData2 = {
        "MRSongNamesArr": MRSongNamesArr,
        "MRNoArr": MRNoArr,
        "MAXy": max(MRNoArr) if (len(MRNoArr) > 0) else 0
    }
    return render_template("AdminDashBoard.html",
                           users=users,
                           Creators=Creators,
                           chartData1=chartData1,
                           chartData2=chartData2,
                           Songs=Scount,
                           albums=albums)


#/Admin/Tracks
@app.route('/Admin/Tracks')
def adminTracks():
  with Session(engine) as session:
    Songs = session.query(Song).all()
    return render_template("AdminAllTracks.html", Songs=Songs, Genre=Genres)


#admin delete tracks
@app.route("/Admin/Tracks/<int:Sid>/delete")
def adminDeleteTrack(Sid):
  with Session(engine) as session:
    song = session.query(Song).filter(Song.Sid == Sid).first()
    songLoc = song.SongLocation
    songCoverImg = song.CoverImgLoc
    songLyrics = song.LyricsLoc
    os.remove(songLoc)
    os.remove(songCoverImg)
    os.remove(songLyrics)
    print("File deleted successfully.")
    session.delete(song)
    session.commit()
    return redirect(url_for("AdminHandler"))


#admin song stream
@app.route("/Admin/Song/<int:Sid>/play")
def Adminplay(Sid):
  with Session(engine) as session:
    SongPlay = session.query(Song).filter(Song.Sid == Sid).first()
    cr = session.query(Creator).filter(Creator.id == Song.Cid).first()
    crDetails = session.query(User).filter(User.id == cr.id).first()
    print(SongPlay.SongLocation)
    Lyrics = ""
    with open(SongPlay.LyricsLoc, 'r') as file:
      Lyrics = file.read()
      # Process the data as needed
    user = session.query(User.id).filter(User.id == SongPlay.Cid).first()
    if (SongPlay):
      return render_template("AdminSongStream.html",
                             Song=SongPlay,
                             cr=cr,
                             crDetails=crDetails,
                             Lyrics=Lyrics)


#admin albums
@app.route("/Admin/Albums")
def AdminAlbums():
  with Session(engine) as session:
    albums = session.query(Albums).all()
    Songs = session.query(Song).all()
    return render_template("AdminAlbums.html", albums=albums, Songs=Songs)


#admin delete album
@app.route("/Admin/Albums/<int:Aid>/delete")
def deleteAlbums(Aid):
  with Session(engine) as session:
    songs = session.query(Song).filter(Song.album_id == Aid).all()
    for i in songs:
      i.album_id = None
    album = session.query(Albums).filter(Albums.Aid == Aid).first()
    session.delete(album)
    session.commit()
    return redirect(url_for("AdminAlbums"))


#admin creator black list
@app.route("/Admin/Creators", methods=["GET", "POST"])
def Creators():
  #GET
  if (request.method == "GET"):
    with Session(engine) as session:
      creatorList = []
      #get the list of creators
      user = session.query(User).all()
      cr = session.query(Creator).all()
      bcrList = []
      bcr = session.query(Creator.id).filter(Creator.blacklist == 1).all()
      for i in bcr:
        for j in i:
          bcrList.append(j)

      print(bcrList)
      print("creators", cr)
      print("blacked", bcr)
      for i in user:
        for j in cr:
          if (i.id == j.id):
            creatorList.append(i)

      #send the list of creators
      print("creator list:", creatorList)
      return render_template("viewCreators.html",
                             creatorsList=creatorList,
                             bcr=bcrList)
  #POST
  if (request.method == "POST"):
    checkedCreators = request.form.getlist(
        "checkedCreators")  #get the list of checked creators
    print("sidofn", checkedCreators)
    with Session(engine) as session:
      cr = session.query(Creator).all()
      print("usodhgnv", cr)
      for i in checkedCreators:
        BlacklistCreator = session.query(Creator).filter(
            Creator.id == i).first()
        #mark them as black list
        BlacklistCreator.blacklist = 1
        print("black listed:", BlacklistCreator)
      for i in cr:
        if ((i.blacklist == 1) and (str(
            i.id) not in checkedCreators)):  #remove creator from blacklist
          i.blacklist = 0
          print("whitelist:", i)
      session.commit()
      return redirect(url_for("AdminHandler"))  #return to dashboard


if (__name__) == "__main__":
  app.run(host="0.0.0.0", port=8080, debug=True)
