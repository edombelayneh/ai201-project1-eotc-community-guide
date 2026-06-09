"""
app.py
EOTC Unofficial Guide — Milestone 5: Gradio Interface

A chat-style web UI over the RAG pipeline:
    question -> retrieve top-k chunks -> grounded generation (Groq) -> answer + sources

Each answer has a "View retrieved context" button that opens a modal showing the
exact chunks (and distance scores) used for that turn.

Usage:
    python app.py
    # then open the local URL Gradio prints (http://127.0.0.1:7860)

Requires GROQ_API_KEY in .env and a vector store built by embed.py.
"""

import gradio as gr

from generate import generate
from retrieve import get_collection, EVAL_QUESTIONS

# Open the ChromaDB collection once at startup and reuse it for every query.
COLLECTION = get_collection()


CSS = """
#chat-area { max-height: 60vh; overflow-y: auto; padding: 4px 8px; }

/* chat bubbles — use theme variables so text stays readable in light AND dark */
.user-row { display: flex; justify-content: flex-end; }
.bot-row  { display: flex; justify-content: flex-start; }
.user-bubble, .bot-bubble {
    max-width: 80%; padding: 12px 16px; border-radius: 16px;
    line-height: 1.5; box-shadow: 0 1px 2px rgba(0,0,0,0.15);
}
/* user: brand color with white text (readable on the blue in any theme) */
.user-bubble, .user-bubble * { background: #2563eb; color: #ffffff !important; }
.user-bubble { border-bottom-right-radius: 4px; }
/* bot: theme's secondary surface + theme's body text color */
.bot-bubble {
    background: var(--background-fill-secondary);
    color: var(--body-text-color);
    border: 1px solid var(--border-color-primary);
    border-bottom-left-radius: 4px;
}
.msg-sources { font-size: 0.8em; color: var(--body-text-color-subdued); margin: 2px 4px 0; }
.ctx-btn { max-width: 220px; margin: 0 4px 8px; }
.empty-hint { color: var(--body-text-color-subdued); text-align: center; padding: 32px 0; }

/* modal overlay */
.modal-overlay {
    position: fixed; inset: 0; z-index: 1000;
    background: rgba(0,0,0,0.55);
    display: flex; align-items: center; justify-content: center;
}
.modal-box {
    background: var(--block-background-fill);
    color: var(--body-text-color);
    width: min(720px, 92vw); max-height: 82vh; overflow-y: auto;
    padding: 24px; border-radius: 14px; box-shadow: 0 10px 40px rgba(0,0,0,0.5);
}
.ctx-chunk {
    background: var(--background-fill-secondary);
    color: var(--body-text-color);
    border: 1px solid var(--border-color-primary);
    border-radius: 10px; padding: 12px 14px; margin-bottom: 10px; font-size: 0.9em;
}
"""


# ─────────────────────────────────────────────────────────────────────────────
# PIPELINE HANDLER
# ─────────────────────────────────────────────────────────────────────────────

def respond(message: str, turns: list[dict]):
    """Run the RAG pipeline and append a turn to the conversation state."""
    message = (message or "").strip()
    if not message:
        return turns, ""
    result = generate(message, collection=COLLECTION)
    turns = turns + [{
        "question": message,
        "answer":   result["answer"],
        "sources":  result["sources"],
        "chunks":   result["chunks"],
    }]
    return turns, ""   # clear the input box


# ─────────────────────────────────────────────────────────────────────────────
# GRADIO INTERFACE
# ─────────────────────────────────────────────────────────────────────────────

with gr.Blocks(title="EOTC Community Guide") as demo:
    history    = gr.State([])     # list of turn dicts
    modal_turn = gr.State(None)   # index of the turn whose context modal is open

    gr.Markdown(
        "## EOTC Community Guide\n"
        "Ask about Ethiopian Orthodox Tewahedo Church theology, fasting, worship, "
        "sacraments, and saints. Answers are grounded only in the indexed documents "
        "and cite their sources."
    )

    # ── Conversation (re-rendered from state) ───────────────────────────────
    with gr.Column(elem_id="chat-area"):
        @gr.render(inputs=history)
        def render_chat(turns):
            if not turns:
                gr.Markdown("Ask a question to begin.", elem_classes="empty-hint")
                return
            for i, turn in enumerate(turns):
                with gr.Row(elem_classes="user-row"):
                    gr.Markdown(turn["question"], elem_classes="user-bubble")
                with gr.Row(elem_classes="bot-row"):
                    gr.Markdown(turn["answer"], elem_classes="bot-bubble")
                if turn["sources"]:
                    gr.Markdown("Sources: " + ", ".join(turn["sources"]),
                                elem_classes="msg-sources")
                ctx_btn = gr.Button("View retrieved context", size="sm",
                                    elem_classes="ctx-btn")
                # capture i so each button opens its own turn's modal
                ctx_btn.click(lambda i=i: i, outputs=modal_turn)

    # ── Input ────────────────────────────────────────────────────────────────
    with gr.Row():
        question_box = gr.Textbox(
            label="", placeholder="Type your question and press Enter...",
            lines=1, scale=5, container=False, autofocus=True,
        )
        send_btn = gr.Button("Send", variant="primary", scale=1)

    gr.Examples(examples=[[q] for q in EVAL_QUESTIONS], inputs=question_box, label="Examples")

    # ── Per-turn context modal (re-rendered from state) ─────────────────────
    @gr.render(inputs=[modal_turn, history])
    def render_modal(mt, turns):
        if mt is None or mt >= len(turns):
            return
        turn = turns[mt]
        with gr.Column(elem_classes="modal-overlay"):
            with gr.Column(elem_classes="modal-box"):
                gr.Markdown(f"### Retrieved context\nFor: *{turn['question']}*")
                for c in turn["chunks"]:
                    gr.Markdown(
                        f"**#{c['rank']} · {c['source']}** "
                        f"(chunk {c['chunk_index']}, distance {c['distance']:.3f})\n\n"
                        f"{c['text'].strip()}",
                        elem_classes="ctx-chunk",
                    )
                close_btn = gr.Button("Close", variant="primary")
                close_btn.click(lambda: None, outputs=modal_turn)

    # ── Wiring ───────────────────────────────────────────────────────────────
    send_btn.click(respond, inputs=[question_box, history], outputs=[history, question_box])
    question_box.submit(respond, inputs=[question_box, history], outputs=[history, question_box])


if __name__ == "__main__":
    demo.launch(css=CSS, theme=gr.themes.Soft())
