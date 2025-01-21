import os
import gradio as gr
import utils
import shared

CHATGPT_MODELS = ["gpt-4o", "gpt-4o-mini"]


with gr.Blocks() as demo:
    gr.Markdown(
        """
        # VisionNoob's Subtitles Translator (English ⏩ Korean) 🌍  

        This demo uses ChatGPT to automatically translate English subtitles into Korean.
        [🌐 Github](https://github.com/visionNoob/kor-eng-auto-subtitle-translation)  
        ⚠️ **For academic research and experimental purposes only. Please use responsibly.**  
        """
    )

    with gr.Tab("🔥 Latest v.0.1"):
        gr.Markdown("# 1️⃣ Activate OpenAI API Key")
        textbox_api_key = gr.Textbox(
            value=os.getenv("OPENAI_API_KEY"),
            placeholder="Enter your OpenAI API Key",
            label="API Key",
            lines=2,
        )
        if shared.client and utils.is_valid_api_key(shared.client):
            button_save_api_key = gr.Button(
                "✅ API Key is successfully set! 🎉",
                variant="primary",
                interactive=False,
            )
        else:
            button_save_api_key = gr.Button("Activate", variant="secondary")

        button_save_api_key.click(
            fn=utils.update_api_key,
            inputs=textbox_api_key,
            outputs=[button_save_api_key],
        )

        gr.Markdown("# 2️⃣ Configuration")
        dropdown_chatgpt_models = gr.Dropdown(
            label="Model", interactive=True, choices=CHATGPT_MODELS
        )
        with gr.Accordion("Prompt", open=True):
            textbox_system_prompt = gr.Textbox(
                show_copy_button=True,
                label="System Prompt",
                lines=5,
                value=shared.system_prompt,
                interactive=True,
            )
            textbox_user_prompt = gr.Textbox(
                show_copy_button=True,
                label="User Prompt",
                lines=5,
                value=shared.user_prompt,
                interactive=True,
            )

        gr.Markdown("# 3️⃣ Upload Subtitles")
        file_output = gr.File(
            label="Upload Subtitles", type="filepath", file_types=[".srt"]
        )

        lines = gr.State()
        with gr.Row():
            with gr.Column():
                gr.Markdown("# 4️⃣ Original Subtitles")
                textbox_input_subtitles = gr.Textbox(
                    show_copy_button=True, label="Input Subtitles"
                )
                button_translate = gr.Button("Translate", variant="stop")
            with gr.Column():
                gr.Markdown("# 5️⃣ Translated Subtitles")
                textbox_output_subtitles = gr.Textbox(
                    show_copy_button=True, label="Translated Subtitles"
                )
                button_download = gr.DownloadButton("Download", variant="secondary")
        file_output.upload(
            utils.upload_file, file_output, [textbox_input_subtitles, lines]
        )

        button_translate.click(
            utils.translate_subtitles,
            [
                lines,
                dropdown_chatgpt_models,
                textbox_system_prompt,
                textbox_user_prompt,
            ],
            [textbox_output_subtitles, button_download],
        )

    with gr.Tab("ℹ️ Info"):
        gr.Markdown(
            """
            ![Image](https://github.com/user-attachments/assets/c98e7481-5e8d-4d19-8811-0f2dd174c35f)
            **Author**: [VisionNoob](https://github.com/visionnoob)
            """
        )
demo.launch()
