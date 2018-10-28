from flask import Flask, request, render_template
import flask_socketio as SocketIO
from pydantic import BaseModel
import uuid
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
socketio = SocketIO.SocketIO(app)

clients = {}
rooms = []

class User(BaseModel):
    name: str
    room_uuid: str


def messageReceived():
    print('message was received!!!')

@socketio.on('connect')
def connected():
    print('Connected {}'.format(request.sid))

@socketio.on('disconnect')
def disconnected():
    print('Disconnected {}'.format(request.sid))

@socketio.on('test')
def send_message(json_msg):
    print(json_msg)
    socketio.emit("message", json_msg)


@socketio.on('message')
def send_message(json_msg):
    print(json_msg)
    msg = json_msg["msg"]
    room = clients[request.sid].room_uuid
    socketio.emit("message", {"user": clients[request.sid].name, "message": msg}, room=room)

@socketio.on('enter_room')
def enter_room(json_msg):
    user = User(**json_msg)
    clients[request.sid] = user
    print(json_msg)
    SocketIO.join_room(user.room_uuid)
    SocketIO.emit(user.name + ' has entered the room.', room=user.room_uuid)


@socketio.on('leave_room')
def leave_room(json):

    print('received my event: ' + str(json))
    for t_sid in clients:
        socketio.emit("message", t_sid, room=t_sid)

@app.route('/create_room', methods=['POST'])
def create_room():
    if request.method == 'POST':
        room_uuid = uuid.uuid4()
        rooms.append({
            "uuid": str(room_uuid),
            "name": request.get_json()["room_name"]
        })
        response = json.dumps({"room_uuid": str(room_uuid)})
        return response

@app.route('/get_rooms', methods=['GET'])
def get_rooms():
    if request.method == 'GET':
        response = json.dumps({"rooms": rooms})
        return response

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    socketio.run(app, debug=True)