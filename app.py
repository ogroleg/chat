from flask import Flask, request, abort, jsonify, render_template, session
from flask_socketio import SocketIO, join_room, disconnect
from db import DB
import helpers
import constants

app = Flask(__name__)

app.config['SECRET_KEY'] = constants.SECRET_KEY
socketio = SocketIO(app)

db = DB()


@app.route('/api/v1/user', methods=['POST'])
def user_create():
    username = request.json.get('username')
    password = request.json.get('password')

    if username is None or password is None:
        return abort(400)

    user_id = db.insert_user(username, password)

    if not user_id:
        return abort(400)

    return jsonify({})


@app.route('/api/v1/token', methods=['POST'])
def token_create():
    username = request.json.get('username')
    password = request.json.get('password')

    if username is None or password is None:
        return abort(400)

    user_id = db.verify_user_password(username, password)

    if not user_id:
        return abort(403)

    token_id, token = db.insert_token(user_id)
    client_token = helpers.pack({'token': token, 'token_id': token_id})

    return jsonify({'token': client_token})


@app.route('/api/v1/token/verify', methods=['POST'])
def token_verify():
    token = request.json.get('token')

    if not is_valid_token(token):
        return abort(403)

    return jsonify({})


def is_valid_token(token):
    if not token:
        return False

    token_data = helpers.unpack(token)
    token_id, token = token_data['token_id'], token_data['token']

    return db.verify_user_token(token_id, token)


@socketio.on('message')
def on_message(data):
    token, text = data.get('token'), data.get('text')

    user_id = is_valid_token(token)

    if not user_id:
        return socketio.emit('logout', {})

    if type(text) is not str or not text.strip():
        return

    message_data = db.insert_new_message(user_id, text)
    message_data['username'] = db.select_username_by_user_id(message_data.pop('user_id'))

    socketio.emit('new_message', {'data': message_data}, broadcast=True, room=constants.ROOM_LOGGEDIN)


@socketio.on('history')
def on_history(data):
    token = data.get('token')

    user_id = is_valid_token(token)

    if not user_id:
        return socketio.emit('logout', {})

    messages_data = db.select_messages(count=constants.CHAT_HISTORY_LEN)[::-1]
    socketio.emit('new_history', {'data': messages_data})


@socketio.on('connect')
def on_connect():
    token = request.args.get('token')

    if is_valid_token(token):
        join_room(constants.ROOM_LOGGEDIN)
    else:
        disconnect(request.sid)


@app.route('/')
def main():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
