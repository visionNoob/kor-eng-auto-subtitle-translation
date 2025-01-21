import os
import openai
import gradio as gr
import shared
import translator


def is_valid_api_key(client):

    try:
        client.models.list()
        return True

    except:
        raise gr.Error("❌ Please enter a valid API Key. 🔄", duration=5)


def init_client(api_key):
    client = openai.OpenAI(api_key=api_key)

    if is_valid_api_key(client):
        return client
    else:
        return None


def update_api_key(api_key):

    if api_key == "":
        raise gr.Error("❌ Please enter a valid API Key. 🔄", duration=5)

    client = init_client(api_key)

    if not client:
        raise gr.Error("❌ Please enter a valid API Key. 🔄", duration=5)
    else:
        os.environ["OPENAI_API_KEY"] = api_key
        shared.client = client
        save_button = gr.Button(
            "✅ API Key is successfully set! 🎉", variant="primary", interactive=False
        )
        return save_button


def upload_file(file):
    """
    Reads an .srt file and returns its contents as text.
    """
    if not file.endswith(".srt"):
        return "❌ Invalid file format. Please upload an .srt file."

    try:
        with open(file, "r", encoding="utf-8") as f:
            shared.save_dir = os.path.dirname(file)
            shared.basename = os.path.basename(file).replace(".srt", "_kor.srt")

            contents = f.read()

        with open(file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        return contents, lines
    except Exception as e:
        return f"⚠️ Error reading file: {e}"


def translate_subtitles(
    subtitles, model, system_prompt, user_prompt, progress=gr.Progress()
):
    """
    Translates the subtitles using the OpenAI API.
    """
    if not subtitles:
        return "❌ Please upload a valid .srt file."

    sub_translator = translator.Translator(shared.client, subtitles)

    progress(0, desc="Starting...")
    translated_subtitles = sub_translator.translate(
        model, system_prompt, user_prompt, progress
    )

    save_dir = os.path.join(shared.save_dir, shared.basename)
    with open(save_dir, "w", encoding="utf-8") as f:
        f.write(translated_subtitles)

    return translated_subtitles, save_dir
