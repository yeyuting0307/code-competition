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
session_path = 'api/sessions'
content_path = "api/contents"

SESSION_URL = os.path.join(jupyter_host, session_path)
CONTENT_URL = os.path.join(jupyter_host, content_path)

headers = {'Authorization' : "Token 9c0aaaef812bf4be4d6d6f76bf64a8a1e497119e4d3ec57d"}

#%%
# ------------------ Create ------------------
# create a new notebook 
new_nb_name = "new_notebook.ipynb"
sub_folder = "Documents/python-socketio"

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

#%%
# ------------------ Read ------------------
nb_name = "new_notebook.ipynb"
sub_folder = "Documents/python-socketio"
nb_path = os.path.join(sub_folder, nb_name)
read_url = os.path.join(CONTENT_URL, nb_path)

response = requests.get(url = read_url, headers=headers)
assert response.status_code == 200, 'Read notebook failed'
notebooks = response.json()
notebooks

# %%
# ------------------ Update ------------------
nb_name = "new_notebook.ipynb"
sub_folder = "Documents/python-socketio"
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
            "name": "sparkkernel", 
            "display_name": "Spark", 
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


# %%
# ------------------ Delete ------------------
nb_name = "new_notebook.ipynb"
sub_folder = "Documents/python-socketio"
nb_path = os.path.join(sub_folder, nb_name)
delete_url = os.path.join(CONTENT_URL, nb_path)

response = requests.delete(url = delete_url, headers=headers)
assert response.status_code == 204, 'Delete notebook failed'
