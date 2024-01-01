# MUSIC STREAMING APP

Introduction:
	 Music Streaming app is a multi user music listening platform, where users can listening songs and enjoy their lesuire time.Users can also register themselves as creators and upload their songs and create albums and monitor their performance on dashboard

# Getting started:

## Requirements:
  To run this app on computer, the system should have the following python libraries installed
  1. flask
  2. flask_sqlalchemy
  3. flask_restful
  4. sqlalchemy

## Installation:
  1. extract the zip file to the desired location
  2. open the command prompt 
  3. navigate to the location where the file is extrated
  4. run the application using command python main.py or flask run

## Usage:
  To use the app, first run the the app using flask run or python main.py while in root folder. now copy the url from the command prompt and open the url in desired browser 	then you will be shown the login page. now, if you already have an account login and go ahead else sign up and register yourself as a user and login to use the app.then you will be 	redirected to the home page .In  this you can play songs view albums,genres etc and create playlists .From the the navigation bar under craetor account the user can switch to 	creator if user is not a creator yet else the creator can upload songs create albums and monitor their's songs and album's performance.


## APIs:
  for this app we created two API's for Songs and Playlists.  
  ### Songs API:  
  for the songs api the route are defined as follows:  
  
    for GET,PUT,DELETE:`/api/user/<int:userid>/song/<int:sid>`  
    for POST:`/api/user/<int:userid>/song `  
  Here,  
  - `userid` is the id given to the user while registering in the app  
  - `sid` is the unique id given to the song while uploaded  
  __Note:__ to PUT,DELETE the song the user id must be belong to the creator of that song  
  ### Playlist API:  
  for the playlists api the routes are defined as follows:  
  
      for GET,PUT,DELETE: "/api/user/<int:Userid>/playlist/<int:Pid>",  
      for POST: "/api/user/<int:Userid>/playlist"  
  Here,  
  - `Userid` is the id given to the user while registering in the app  
  - `Pid` is the unique id given to the Playlist while creator  
