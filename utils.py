import os
import openai
import gradio as gr


def is_valid_api_key(client):

    try:
        client.models.list()

    except openai.AuthenticationError:
        return False
    else:
        return True


def init_client(api_key):
    client = openai.OpenAI(api_key=api_key)

    if is_valid_api_key(client):
        return client
    else:
        return None
