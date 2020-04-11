from threading import Lock
from flask import Flask, render_template, session, request, copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
from difflib import SequenceMatcher
import time

#sorry, im kinda lazy and dumb, so only websocket 🙃 🙃 🙃 🙃 🙃 

async_mode = "threading"

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
messages=[]

socketio = SocketIO(app, async_mode=async_mode)

thread_websocket = None
thread_websocket_lock = Lock()
def background_thread_websockets():
    while True:
        socketio.sleep(5)
        socketio.emit('my_response',
                      {'data': 'Bot: I\'m bored! Write something!!!'},
                      namespace='/test')

def dialogue(message):
    emit('my_response', {'data': "Me:"+message['data']})
    if str(message['data']).strip()!="Connected!":
        messages.append("Me:"+message['data'])
        message = str(message['data']).lower()
        options_map = {
            1: ("currency","money","dollar","usd"),
            2: ("weather","saint-petersburg"),
            3: ("sport","football"),
            4: ("how are you?","whats up?"),
            5: ("hello", "hi", "greetings"),
            6: ("you are just a bot","stupid","dumb"),
            7: ("joke","laugh"),
            8: ("bye","see you","good night"),
            9: ("help","commands","what can you do?")
            }

        match=0.0
        for option in options_map:
            for word in options_map[option]:
                match_temp = SequenceMatcher(lambda x: x == " ",message,word).ratio()
                if match_temp>match:
                    match=match_temp
                    key = option
        if match<0.6:
            key=10 
        if key==1: #currency
            msg = "Bot: Ruble is still stable"
        elif key==2: #weather
            msg = "Bot: There is no cloud in the sky"
        elif key==3: #sport
            msg = "Bot: Because of coronavirus there is no sport (("
        elif key==4: #how are you?
            msg = "Bot: Working, and you?"
        elif key==5: #hello
            msg = "Bot: Hi!"
        elif key==6: #you are just a bot
            msg = "Bot: Can a bot write a symphony? Can a bot turn a... canvas into a beautiful masterpiece?"
        elif key==7: #joke
            msg = "Bot: How do robots eat guacamole?"
            emit('my_response', {'data': msg})
            messages.append(msg)
            msg = "Bot: With microchips!"
        elif key==8: #bye
            msg = "Bot: See you!"
        elif key==9: #help
            msg = "Bot: Help page:"
            emit('my_response', {'data': msg})
            messages.append(msg)
            msg = "Bot: Available topics: greetengs, currency, weather, sport, \"how are you?\", \"you are just a bot\", joke, bye, help page"
        elif key==10: #sorry
            msg = "Bot: Sorry, i'm kinda dumb 🙃"
        messages.append(msg)
        emit('my_response', {'data': msg})
    else:
        emit('my_response', {'data': "Previous messages:"})
        for message in messages:
            emit('my_response', {'data': message})
        emit('my_response', {'data': "Bot: Help page:"})
        emit('my_response', {'data': "Bot: Available topics: greetengs, currency, weather, sport, \"how are you?\", \"you are just a bot\", joke, bye, help page"})
        emit('my_response', {'data': "New messages:"})


@app.route('/')
def index():
    return render_template('websockets.html', async_mode=socketio.async_mode)

@socketio.on('my_event', namespace='/test')
def test_message(message):
    dialogue(message)
    global thread_websocket
    with thread_websocket_lock:
        if thread_websocket is None:
            thread_websocket = socketio.start_background_task(background_thread_websockets)
    
@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my_response', {'data': 'Bot: Connected'})


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0",port="31337",debug=True)
