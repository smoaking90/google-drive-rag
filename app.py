import gradio as gr

from answer import answer_question


def ask_knowledge_base(question):
    question = question.strip()

    if not question:
        return "Please enter a question.", ""

    answer, retrieved_documents = answer_question(question)

    source_lines = []
    seen_sources = set()

    for document in retrieved_documents:
        metadata = document.metadata

        file_name = metadata.get(
            "file_name",
            "Unknown file",
        )

        page = metadata.get("page")
        source_url = metadata.get("source_url")

        source_key = (file_name, page)

        if source_key in seen_sources:
            continue

        seen_sources.add(source_key)

        if isinstance(page, int):
            # PyPDFLoader uses zero-based page numbers.
            source_label = f"{file_name}, page {page + 1}"
        else:
            source_label = file_name

        if source_url:
            source_lines.append(
                f"- [{source_label}]({source_url})"
            )
        else:
            source_lines.append(f"- {source_label}")

    sources = "\n".join(source_lines)

    return answer, sources


with gr.Blocks(title="Google Drive Knowledge Worker") as app:
    gr.Markdown(
        """
        # Google Drive Knowledge Worker

        Ask questions about the documents indexed from your
        Google Drive knowledge-base folder.
        """
    )

    question_input = gr.Textbox(
        label="Question",
        placeholder="What would you like to know?",
        lines=2,
    )

    ask_button = gr.Button(
        "Ask",
        variant="primary",
    )

    answer_output = gr.Markdown(
        label="Answer",
    )

    sources_output = gr.Markdown(
        label="Retrieved sources",
    )

    ask_button.click(
        fn=ask_knowledge_base,
        inputs=question_input,
        outputs=[
            answer_output,
            sources_output,
        ],
    )

    question_input.submit(
        fn=ask_knowledge_base,
        inputs=question_input,
        outputs=[
            answer_output,
            sources_output,
        ],
    )


if __name__ == "__main__":
    app.queue()
    app.launch(inbrowser=True)