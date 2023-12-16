#%%
import io
import os
import json
import requests
import inspect
import contextlib
import uuid
import time
import datetime
from websocket import create_connection


class Jupyter:
    ''' 
    https://jupyter-server.readthedocs.io/en/latest/developers/rest-api.html
    '''
    def __init__(self, 
            jupyter_host = 'http://127.0.0.1:8888', 
            jupyter_websocket_host = 'ws://127.0.0.1:8888',
            jupyter_token = None
        ):
        

        session_path = 'api/sessions'
        content_path = "api/contents"
        kernel_path = "api/kernels"

        self.JUPYTER_TOKEN = jupyter_token
        self.COMMAND_URL = os.path.join(jupyter_websocket_host, kernel_path)
        self.CONTENT_URL = os.path.join(jupyter_host, content_path)
        self.KERNEL_URL = os.path.join(jupyter_host, kernel_path)
        self.SESSION_URL = os.path.join(jupyter_host, session_path)

        self.headers = {'Authorization' : f"Token {jupyter_token}"}
        self.curr_kernel_id = None
    def create_notebook(self, new_nb_name = "new_notebook.ipynb", sub_folder = "python-socketio/notebooks"):
        # create a new notebook 

        create_url = os.path.join(self.CONTENT_URL, sub_folder)

        data = json.dumps({
            "type": "notebook"
        })

        response = requests.post(url = create_url, headers=self.headers, data=data)
        print('create', response)
        assert response.status_code == 201, 'Create notebook failed'
        new_notebook = response.json()

        # rename a notebook
        default_nb_name = new_notebook.get('name')
        new_nb_path = os.path.join(sub_folder, new_nb_name)
        rename_url = os.path.join(self.CONTENT_URL, sub_folder, default_nb_name)

        data=json.dumps({"path" : new_nb_path})
        response = requests.patch(url = rename_url, headers=self.headers, data=data)
        assert response.status_code == 200, 'Rename failed, either old_nb not existed or new_nb already existed'
        new_notebook = response.json()

        return new_notebook

    def read_notebook(self, nb_name = "new_notebook.ipynb", sub_folder = "python-socketio/notebooks"):
        
        nb_path = os.path.join(sub_folder, nb_name)
        read_url = os.path.join(self.CONTENT_URL, nb_path)

        response = requests.get(url = read_url, headers=self.headers)
        print('read', response)
        assert response.status_code == 200, 'Read notebook failed'
        notebooks = response.json()
        return notebooks

    def update_notebook(
            self,
            input_code = "",
            output_text = "",
            nb_name = "new_notebook.ipynb",
            sub_folder = "python-socketio/notebooks",
        ):
        
        nb_path = os.path.join(sub_folder, nb_name)
        update_url = os.path.join(self.CONTENT_URL, nb_path)

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
                    "source": f"""{input_code}""", 
                    "metadata": { 
                        "collapsed": True, 
                        "scrolled": "auto", 
                    },
                    "execution_count": None, 
                    "outputs": [
                        {
                            "output_type": "stream",
                            "name": "stdout",  # or stderr
                            "text": f"""{output_text}""",
                        },
                    ]
                }
            ]
        }

        data = json.dumps({
            "type": "notebook", 
            "content": content
        })

        response = requests.put(url = update_url, headers=self.headers, data = data)
        assert response.status_code == 200, 'Update notebook failed'
        return response

    def delete_notebook(self, nb_name , sub_folder = "python-socketio/notebooks"):
        
        nb_path = os.path.join(sub_folder, nb_name)
        delete_url = os.path.join(self.CONTENT_URL, nb_path)

        response = requests.delete(url = delete_url, headers=self.headers)
        assert response.status_code == 204, 'Delete notebook failed'

    def create_kernel(self, kernel_name = "python3", kernel_path = "/usr/local/bin/python3"):
        data = {
            "name" : kernel_name,
            "path" : kernel_path
        }
        response = requests.post(url = self.KERNEL_URL, headers = self.headers, json = data)
        response
        assert response.status_code == 201, 'Create Kernel failed'
        kernel = response.json()
        return kernel
    
    def get_kernels(self):
        response = requests.get(url = self.KERNEL_URL, headers=self.headers)
        assert response.status_code == 200, 'Get Kernel failed'
        kernels = response.json()
        return kernels

    def interrupt_kernel(self, kernel_id):
        interrupt_url = os.path.join(self.KERNEL_URL, kernel_id, "interrupt")
        response = requests.post(url = interrupt_url, headers=self.headers)
        return response
    
    def delete_kernel(self, kernel_id):
        delete_url = os.path.join(self.KERNEL_URL, kernel_id)
        response = requests.delete(url = delete_url, headers=self.headers)
        assert response.status_code == 204, 'Delete Kernel failed'
        return response
    
    def create_session(self, kernel, notebook_path):
        data = {
            "id" : uuid.uuid1().hex,
            "kernel" : kernel,
            "name" : uuid.uuid1().hex,
            "path" : notebook_path,
            "type" : "notebook"
        }
        response = requests.post(url = self.SESSION_URL, headers = self.headers, json = data)
        assert response.status_code == 201, 'Create Session failed'
        session = response.json()
        return session

    def get_sessions(self):
        response = requests.get(url = self.SESSION_URL, headers=self.headers)
        assert response.status_code == 200, 'Get Session failed'
        sessions = response.json()
        return sessions
    
    def websocket_connect(self, session_id, kernel_id):
        ws_url = os.path.join(
            self.COMMAND_URL, 
            kernel_id, 
            f"channels?session_id={session_id}&token={self.JUPYTER_TOKEN}")

        ws = create_connection(
            url = ws_url, 
            headers = self.headers
        )
        self.curr_kernel_id = kernel_id
        return ws
    
    def ws_send_exec_code(
            self, ws, code, 
            msg_id = None, 
            username = None,
            session = None
        ):
        msg_type = 'execute_request'
        content = {'code':code, 'silent':False}
        hdr = { 
            'msg_id' : msg_id or uuid.uuid1().hex, 
            'username': username or uuid.uuid1().hex, 
            'session': session or uuid.uuid1().hex, 
            'data': datetime.datetime.now().isoformat(),
            'msg_type': msg_type,
            'version' : '5.0' }
        msg = {   
            "header": hdr,
            "parent_header": hdr,
            "metadata": {},
            "content": content,
            "channel" : "shell" # shell, iopub
        }
        valid_req = json.dumps(msg)
        ws.send(valid_req)
        return msg
    
    def ws_recv_exec_result(self, ws, time_out = 1):
        output = {
            "type" : "",
            "code_result" : {}
        }
        S = time.time()
        while True:
            response = ws.recv()
            data_json = json.loads(response)
            msg_type = data_json.get('msg_type')
            E = time.time()
            if E-S > time_out:
                output.update({
                    "type" : "timeout",
                    "code_result" : data_json
                })
                try:
                    print(f"Try to interrupt: {self.curr_kernel_id}")
                    self.interrupt_kernel(self.curr_kernel_id)
                except Exception as e:
                    print(f"Intterupt Fail with {self.curr_kernel_id}:{e}")
                break
            if msg_type == 'status':
                status = data_json.get('content', {}).get('execution_state') # idle, busy, ...
                if status == "idle":
                    print("Finished")
                    pass
                elif status == "busy":
                    pass
            elif msg_type == 'execute_input':
                # S = time.time() # reset timer is for fair
                input_code = data_json\
                    .get('content', {})\
                    .get('code', "")
                print(f"Revied input code: {input_code}")
            elif msg_type == 'stream':
                output.update({
                    "type" : "answer",
                    "code_result" : data_json
                })
                break
            else:
                pass
        return output
        

