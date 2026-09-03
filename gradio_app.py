import gradio as gr
import os
from src.pipeline import VideoPipeline

# Global state
pipeline = None
table_name = None


def process_video(video_path):
    """Process uploaded video."""
    global pipeline, table_name

    if not video_path:
        return "No video uploaded", None

    try:
        pipeline = VideoPipeline("config/default.yaml")
        result = pipeline.process(video_path)
        table_name = result["table_name"]

        return (
            f"✅ Processing complete!\n"
            f"Scenes detected: {result['num_scenes']}\n"
            f"Table: {table_name}\n"
            f"Time: {result['elapsed_time']:.2f}s",
            table_name
        )
    except Exception as e:
        return f"❌ Error: {str(e)}", None


def search_scenes(query, table):
    """Search for scenes."""
    if not table or not pipeline:
        return "No video processed yet"

    try:
        results = pipeline.search([query], table, batch_process=False)

        if results and results[0]:
            output = f"Found {len(results[0])} matches:\n\n"
            for r in results[0][:10]:
                output += (
                    f"Scene {r.get('scene_id')}: "
                    f"{r.get('start_time', 0):.2f}s - {r.get('end_time', 0):.2f}s "
                    f"({r.get('duration', 0):.2f}s)\n"
                )
            return output
        else:
            return "No matching scenes found"
    except Exception as e:
        return f"Error: {str(e)}"


# Create Gradio interface
with gr.Blocks(title="Video RAG Engine") as demo:
    gr.Markdown("# 🎬 Video RAG Engine")
    gr.Markdown("AI-Powered Scene Detection & Clip Extraction")

    with gr.Tab("Process Video"):
        video_input = gr.Video(label="Upload Video")
        process_btn = gr.Button("Process", variant="primary")
        process_output = gr.Textbox(label="Status", lines=4)
        table_output = gr.Textbox(label="Table Name", visible=False)

        process_btn.click(
            fn=process_video,
            inputs=video_input,
            outputs=[process_output, table_output]
        )

    with gr.Tab("Search Scenes"):
        query_input = gr.Textbox(label="Search Query", placeholder="e.g., car, drone shot, person")
        table_input = gr.Textbox(label="Table Name")
        search_btn = gr.Button("Search", variant="primary")
        search_output = gr.Textbox(label="Results", lines=10)

        search_btn.click(
            fn=search_scenes,
            inputs=[query_input, table_input],
            outputs=search_output
        )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=5000,
        share=False
    )
