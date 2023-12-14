#%%
import io
import os
import json
import requests
import inspect
import contextlib

#%%

# https://docs.qubole.com/en/latest/rest-api/jupy-notebook-api/index.html

jupyter_host = 'http://localhost:8888'
jupyter_websocket_host = 'ws://localhost:8888'
token = "060c4a8ca6a463676e662362eebe510fe7f0dfa941953b70"

headers = {
    'Authorization' : f"Token {token}"
}


session_path = 'api/sessions'
content_path = "api/contents"
kernel_path = "api/kernels"

COMMAND_URL = os.path.join(jupyter_websocket_host, kernel_path)
CONTENT_URL = os.path.join(jupyter_host, content_path)
KERNEL_URL = os.path.join(jupyter_host, kernel_path)
SESSION_URL = os.path.join(jupyter_host, session_path)


#%%
# ------------------ Create ------------------
# create a new notebook 
new_nb_name = "new_notebook.ipynb"
sub_folder = "python-socketio"

if not os.path.exists(os.path.join('..','..', sub_folder, new_nb_name)):

    create_url = os.path.join(CONTENT_URL, sub_folder)

    data = json.dumps({
        "type": "notebook"
    })

    response = requests.post(url = create_url, headers=headers, data=data)
    assert response.status_code == 201, 'Create notebook failed'
    new_notebook = response.json()

    # rename a notebook
    default_nb_name = new_notebook.get('name')
    new_nb_path = os.path.join(sub_folder, new_nb_name)
    rename_url = os.path.join(CONTENT_URL, sub_folder, default_nb_name)

    data=json.dumps({"path" : new_nb_path})
    response = requests.patch(url = rename_url, headers=headers, data=data)
    assert response.status_code == 200, 'Rename failed, either old_nb not existed or new_nb already existed'
    new_notebook = response.json()
    new_notebook
else:
    print('Notebook already existed')
#%%
# ------------------ Read ------------------
nb_name = "new_notebook.ipynb"
sub_folder = "python-socketio"
nb_path = os.path.join(sub_folder, nb_name)
read_url = os.path.join(CONTENT_URL, nb_path)

response = requests.get(url = read_url, headers=headers)
assert response.status_code == 200, 'Read notebook failed'
notebooks = response.json()
notebooks


# %%
# ------------------ Update ------------------
nb_name = "new_notebook.ipynb"
sub_folder = "python-socketio"
nb_path = os.path.join(sub_folder, nb_name)
update_url = os.path.join(CONTENT_URL, nb_path)


def fn(n):
    if n == 1:
        return 1
    if n == 2:
        return 1
    return fn(n-1) + fn(n-2)

code = f'''# fabonacci
{inspect.getsource(fn)}
for i in range(1, 30):
    print(i, fn(i))
'''

output_stream = io.StringIO()
with contextlib.redirect_stdout(output_stream):
    exec(code)
output = output_stream.getvalue()

# https://nbformat.readthedocs.io/en/latest/format_description.html
content = {"metadata": {
        "kernelspec": {
            "name": "python3", 
            "display_name": "Python3", 
            "language": "python"
        },
        "language_info": {
            "name": "python",
            "version": "3.9",
        }
    }, 
    "nbformat_minor": 4, 
    "nbformat": 4,
    "cells": [
        {
            "cell_type": "code", 
            "source": code, 
            "metadata": { 
                "collapsed": True,  # whether the output of the cell is collapsed,
                "scrolled": "auto",  # any of true, false or "auto"}, 
            },
            "execution_count": None, 
            "outputs": [
                {
                    "output_type": "stream",
                    "name": "stdout",  # or stderr
                    "text": f"{output}",
                },
            ]
        }
    ]
}

data = json.dumps({
    "type": "notebook", 
    "content": content
})

response = requests.put(url = update_url, headers=headers, data = data)
assert response.status_code == 200, 'Update notebook failed'

#%%

# ------------------ Create Kernel ------------------
data = {
    "name" : "python3",
    "path" : "/usr/local/bin/python3"
}
response = requests.post(url = KERNEL_URL, headers = headers, json = data)
response
assert response.status_code == 201, 'Create Kernel failed'
kernels = response.json()
kernels

#%%
# ------------------ Get Kernel ------------------
response = requests.get(url = KERNEL_URL, headers=headers)
assert response.status_code == 200, 'Get Kernel failed'
kernels = response.json()
print(kernels)

latest_kernel = kernels[-1] if kernels else None
latest_kernel


#%%
# ------------------ Create Session ------------------
import uuid
data = {
    "id" : uuid.uuid1().hex,
    "kernel" : latest_kernel,
    "name" : uuid.uuid1().hex,
    "path" : os.path.join("..", "..",notebooks.get('path')),
    "type" : "notebook"
}
response = requests.post(url = SESSION_URL, headers=headers, json=data)
assert response.status_code == 201, 'Create Session failed'
new_session = response.json()
new_session

#%%
# ------------------ Get Session ------------------
response = requests.get(url = SESSION_URL, headers=headers)
assert response.status_code == 200, 'Get Session failed'
sessions = response.json()
print(sessions)

latest_session = sessions[-1] if sessions else None
latest_session

#%%
# ------------------ Run Session ------------------

from websocket import create_connection

session_id =  latest_session.get('id')
kernel_id = latest_session.get('kernel').get('id')

ws_url = os.path.join(COMMAND_URL, kernel_id, f"channels?session_id={session_id}")
print(ws_url)

ws = create_connection(
    url = ws_url, 
    headers = headers
)
ws

#%%
# https://stackoverflow.com/questions/54475896/interact-with-jupyter-notebooks-via-api
import datetime
def send_execute_request(code):
    msg_type = 'execute_request'
    content = { 'code' : code, 'silent':False }
    hdr = { 'msg_id' : uuid.uuid1().hex, 
        'username': 'test', 
        'session': uuid.uuid1().hex, 
        'data': datetime.datetime.now().isoformat(),
        'msg_type': msg_type,
        'version' : '5.0' }
    msg = { 'header': hdr, 'parent_header': hdr, 
        'metadata': {},
        'content': content }
    return msg

#%%
# %%
# ------------------ Delete ------------------
nb_name = "new_notebook.ipynb"
sub_folder = "python-socketio"
nb_path = os.path.join(sub_folder, nb_name)
delete_url = os.path.join(CONTENT_URL, nb_path)

response = requests.delete(url = delete_url, headers=headers)
assert response.status_code == 204, 'Delete notebook failed'
