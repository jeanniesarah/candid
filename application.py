import os

from collections import deque

from flask import Flask, render_template, session, request, redirect
from flask_socketio import SocketIO, send, emit, join_room, leave_room

from helpers import login_required

app = Flask(__name__)
app.config["SECRET_KEY"] = "my secret key"
socketio = SocketIO(app)

# Keep track of channels created 
channelsCreated = []

# Keep track of users logged in
usersLogged = []

channelsMessages = dict()

@app.route("/")
@login_required
def index():

    return render_template("index.html", channels=channelsCreated)

@app.route("/signin", methods=['GET','POST'])
def signin():
    ''' Save alter ego username as a session after user submits sign in form '''

    # Forget username/alter ego
    session.clear()

    username = request.form.get("username")
    
    if request.method == "POST":

        if len(username) < 1 or username is '':
            return render_template("error.html", message="username can't be empty.")

        if username in usersLogged:
            return render_template("error.html", message="that username already exists!")                   
        
        usersLogged.append(username)

        session['username'] = username

        # Save user session on cookie when browser is closed
        session.permanent = True

        return redirect("/")
    else:
        return render_template("signin.html")

@app.route("/logout", methods=['GET'])
def logout():
    """ Log out user from list & delete cookie"""

    # Remove from list
    try:
        usersLogged.remove(session['username'])
    except ValueError:
        pass

    # Delete cookie
    session.clear()

    return redirect("/")

@app.route("/create", methods=['GET','POST'])
def create():
    """ Create channel and redirect to channel page """

    # Get channel name from form
    newChannel = request.form.get("channel")

    if request.method == "POST":

        if newChannel in channelsCreated:
            return render_template("error.html", message="that channel already exists!")
        
        # Add channel to global list of channels
        channelsCreated.append(newChannel)

        # Add channel to global dict of channels with messages
        channelsMessages[newChannel] = deque()

        return redirect("/channels/" + newChannel)
    
    else:

        return render_template("create.html", channels = channelsCreated)

@app.route("/channels/<channel>", methods=['GET','POST'])
@login_required
def enter_channel(channel):
    """ Show channel page to send & receive messages """

    # Update current channel that user's on
    session['current_channel'] = channel

    if request.method == "POST":
        
        return redirect("/")
    else:
        return render_template("channel.html", channels= channelsCreated, messages=channelsMessages[channel])

@socketio.on("joined", namespace='/')
def joined():
    """ Announce user has joined channel """
    
    # Save current channel to room
    room = session.get('current_channel')

    join_room(room)
    
    emit('status', {
        'userJoined': session.get('username'),
        'channel': room,
        'msg': session.get('username') + ' has entered the channel'}, 
        room=room)

@socketio.on("left", namespace='/')
def left():
    """ Announce user has left channel """

    room = session.get('current_channel')

    leave_room(room)

    emit('status', {
        'msg': session.get('username') + ' has left the channel'}, 
        room=room)

@socketio.on('send message')
def send_msg(msg, timestamp):
    """ Receive message with timestamp & broadcast on channel """

    # Broadcast only to users on same channel
    room = session.get('current_channel')

    # Save 100 messages and pass them when a user joins a specific channel

    if len(channelsMessages[room]) > 100:
        # Pop oldest message
        channelsMessages[room].popleft()

    channelsMessages[room].append([timestamp, session.get('username'), msg])

    emit('announce message', {
        'user': session.get('username'),
        'timestamp': timestamp,
        'msg': msg}, 
        room=room)