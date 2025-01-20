import os
import gradio as gr
import utils
import shared


def update_api_key(api_key):

    client = utils.init_client(api_key)

    if not client:
        raise ValueError("❌ Invalid API Key.  Please check and try again. 🔄")
    else:
        os.environ["OPENAI_API_KEY"] = api_key
        shared.client = client
        save_button = gr.Button(
            "✅ API Key is successfully set! 🎉", variant="primary", interactive=False
        )
        return save_button


with gr.Blocks() as demo:
    gr.Markdown("# 1️⃣ Activate OpenAI API Key")
    openapi_key = gr.Textbox(
        value=os.getenv("OPENAI_API_KEY"),
        placeholder="Enter your OpenAI API Key",
        label="API Key",
        lines=2,
    )
    if shared.client and utils.is_valid_api_key(shared.client):
        save_button = gr.Button(
            "✅ API Key is successfully set! 🎉", variant="primary", interactive=False
        )
    else:
        save_button = gr.Button("Activate", variant="secondary")

    save_button.click(
        fn=update_api_key,
        inputs=openapi_key,
        outputs=[save_button],
    )

    status_markdown = gr.Markdown("Please enter your OpenAI API Key.")

    gr.Markdown("# 2️⃣ Configuration")
    dropdown_models = gr.Dropdown(label="Model", interactive=True)

demo.launch()
