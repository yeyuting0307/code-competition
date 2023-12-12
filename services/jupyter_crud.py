#%%
import io
import os
import json
import requests
import inspect
import contextlib

from .code_test import pass_cases
from .cases.test1 import TestCase
selected_test = TestCase()
test_cases = selected_test.get_answers()
class Jupyter:
    def __init__(self, jupyter_host = 'http://127.0.0.1:8888', jupyter_token = None):

        session_path = 'api/sessions'
        content_path = "api/contents"

        self.SESSION_URL = os.path.join(jupyter_host, session_path)
        self.CONTENT_URL = os.path.join(jupyter_host, content_path)
        
        self.headers = {'Authorization' : f"Token {jupyter_token}"}

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
            nb_name = "new_notebook.ipynb",
            sub_folder = "python-socketio/notebooks",
            code = ""
        ):
        
        nb_path = os.path.join(sub_folder, nb_name)
        update_url = os.path.join(self.CONTENT_URL, nb_path)
        
        test_results = pass_cases(code, test_cases)

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
                        "collapsed": True, 
                        "scrolled": "auto", 
                    },
                    "execution_count": None, 
                    "outputs": [
                        {
                            "output_type": "stream",
                            "name": "stdout",  # or stderr
                            "text": f"{test_results}",
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
        return test_results

    def delete_notebook(self, nb_name = "new_notebook.ipynb", sub_folder = "python-socketio/notebooks"):
        
        nb_path = os.path.join(sub_folder, nb_name)
        delete_url = os.path.join(self.CONTENT_URL, nb_path)

        response = requests.delete(url = delete_url, headers=self.headers)
        assert response.status_code == 204, 'Delete notebook failed'
