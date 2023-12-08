from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__, template_folder = "templates")
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    # TODO: create notebook
    print('Client connected 😀')

@socketio.on('disconnect')
def handle_disconnect():
    # TODO: delete notebook
    print('Client disconnected 🥲')

@socketio.on('message')
def handle_message(message):
    # TODO: update notebook
    print('received message: ' + message)
    response_message = message.upper()
    emit('response_message', {'data': response_message})

if __name__ == '__main__':
    socketio.run(app, debug=True)

