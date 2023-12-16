import os
import time
import stat
import dotenv
import uuid
from hashlib import sha1
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from services.jupyter_conn import Jupyter
from code_cases.fibonacci import TestCase

dotenv.load_dotenv()
JUPYTER_TOKEN = os.environ.get("JUPYTER_NOTEBOOK_TOKEN", "060c4a8ca6a463676e662362eebe510fe7f0dfa941953b70")
JUPYTER_TOKEN = "060c4a8ca6a463676e662362eebe510fe7f0dfa941953b70"
app = Flask(__name__, template_folder = "templates")
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
jupyter = Jupyter(jupyter_token=JUPYTER_TOKEN)
cache = {}

test_cases = TestCase().gen_test_case()
print('test_cases', test_cases)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('cache', cache)
    print('Client connected 😀')

    cookie = list(request.cookies.to_dict().values())[0]
    if cookie not in cache:
        nb_name = f"{sha1(cookie.encode()).hexdigest()}.ipynb"
        cache[cookie] = {"nb_name" : nb_name}

        if os.path.exists(os.path.join("notebooks", nb_name)):
            print(f"{nb_name} existed!")
        else:
            jupyter.create_notebook(new_nb_name=nb_name)
            os.chmod(os.path.join("notebooks", nb_name), stat.S_IRWXU)
    print('cookie: ', cache[cookie])

    cookie_nb = jupyter.read_notebook(nb_name=cache[cookie].get("nb_name"))
    print(cookie_nb)
    cells = cookie_nb.get('content', {}).get('cells', [])
    source, output = "", ""
    if cells != []:
        source = cells[0].get('source', '')
        output = cells[0].get('outputs', [{}])[0].get('text', '')
    emit('read_code', {'data': source})
    emit('response_message', {'data': output})
    

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected 🥲')


@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)
    cookie = list(request.cookies.to_dict().values())[0]
    nb_name = cache[cookie].get("nb_name")

    ## update notebook code block
    jupyter.update_notebook(
        nb_name = nb_name,
        input_code = message
    )
    print("update_notebook", message)

    ## get or create kernel for user
    kernel = cache[cookie].get('kernel')
    if kernel is None:
        kernel = jupyter.create_kernel()
        cache[cookie]['kernel'] = kernel
    print("kernel", kernel)

    ## get or create session for user
    session = cache[cookie].get('session')
    if session is None:
        session = jupyter.create_session(
            kernel=kernel, notebook_path=nb_name)
        cache[cookie]['session'] = session
    print("session", session)

    ## create ws connection
    session_id = session.get('id')
    kernel_id = kernel.get('id')
    ws = jupyter.websocket_connect(session_id, kernel_id)
    print("ws", ws)

    ## exec code and test result
    user_code = message
    eval_text = ""
    correct_map = {}
    pass_count = 0

    for idx, (fn_input, correct_answer) in enumerate(test_cases):
        
        test_input = f"print(fn({fn_input}))"
        run_code = f"""# Run Test 
{user_code}
{test_input}
"""
        print("correct_map", correct_map)
        msg_id = uuid.uuid1().hex
        print("< msg_id >", msg_id)
        correct_map.update({msg_id: correct_answer})
        jupyter.ws_send_exec_code(ws, run_code, msg_id = msg_id)

        ans_object = jupyter.ws_recv_exec_result(ws)
        print("ans_object", ans_object)
        if ans_object.get('type') == "timeout":
            user_answer = "Exceed Timeout"
            code_msg_id = ans_object\
                .get('code_result', {})\
                .get('msg_id')
        else:
            code_result = ans_object.get('code_result', {})
            code_msg_id = code_result\
                .get('parent_header', {})\
                .get('msg_id', "")
            user_answer = code_result\
                .get('content', {})\
                .get('text', '').strip()
        
        print("< code_msg_id >", code_msg_id)
        check_correct_answer = correct_map.get(code_msg_id)

        print(f"{user_answer} vs {check_correct_answer}")
        
        if str(user_answer) == str(check_correct_answer):
            eval_text += f"[🟢] Test_{idx+1:03d}\n\t"
            pass_count += 1
        else:
            eval_text += f"[🔴] Test_{idx+1:03d}\n\t"

        eval_text += f"Input: {fn_input}  "+ \
                    f"Output: {user_answer}  "+ \
                    f"Expected: {correct_answer}\n"

    eval_text = f"Total Pass: {pass_count} / {len(test_cases)} " \
                + f"{'🎉' if pass_count == len(test_cases) else '🤔'}\n"\
                + "="*30 + "\n" + eval_text
    ## update notebook output block
    jupyter.update_notebook(
        nb_name = nb_name,
        input_code = message,
        output_text = eval_text
    )

    ## show output to user
    emit('response_message', {'data': eval_text})

if __name__ == '__main__':
    socketio.run(app, debug=True)

