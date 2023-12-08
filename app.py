from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__, template_folder = "templates")
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected 😀')


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected 🥲')

if __name__ == '__main__':
    socketio.run(app, debug=True)

