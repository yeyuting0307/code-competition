import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from services.jupyter_crud import Jupyter
import dotenv
from hashlib import sha1

dotenv.load_dotenv()
JUPYTER_TOKEN = os.environ.get("JUPYTER_NOTEBOOK_TOKEN", "")

app = Flask(__name__, template_folder = "templates")
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
jupyter = Jupyter(jupyter_token=JUPYTER_TOKEN)
cache = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected 😀')
    cookie = list(request.cookies.to_dict().values())[0]

    if cookie not in cache:
        nb_name = f"{sha1(cookie.encode()).hexdigest()}.ipynb"
        cache[cookie] = nb_name 
        if os.path.exists(os.path.join("notebooks", nb_name)):
            print(f"{nb_name} existed!")
        else:
            jupyter.create_notebook(new_nb_name=nb_name)
    cookie_nb = jupyter.read_notebook(nb_name=cache[cookie])
    print(cookie_nb)
    

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

