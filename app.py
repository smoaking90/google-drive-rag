import gradio as gr

from answer import answer_question


def format_sources(documents):
    source_lines = []
    seen_sources = set()

    for document in documents:
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
            label = f"{file_name}, page {page + 1}"
        else:
            label = file_name

        if source_url:
            source_lines.append(
                f"- [{label}]({source_url})"
            )
        else:
            source_lines.append(f"- {label}")

    return "\n".join(source_lines)


def chat(message, history):
    answer, retrieved_documents = answer_question(
        question=message,
        history=history,
    )

    sources = format_sources(retrieved_documents)

    return (
        f"{answer}\n\n"
        f"---\n\n"
        f"**Retrieved sources**\n\n"
        f"{sources}"
    )


app = gr.ChatInterface(
    fn=chat,
    title="Google Drive Knowledge Worker",
    description=(
        "Ask questions about the documents indexed from "
        "your Google Drive knowledge-base folder."
    ),
    save_history=True,
)


if __name__ == "__main__":
    app.queue()
    app.launch(inbrowser=True)