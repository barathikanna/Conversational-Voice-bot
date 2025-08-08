import argparse
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama
import json

from get_embedding_function import get_embedding_function

CHROMA_PATH = r"D:\NSUB\Prototype\chroma"

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Here is the chat history, use it to understand the context of the new question:

{chat_history}

---

Answer the question like telling a 10 year old based on the above context and chat history.
IMPORTANT: Your entire response must be a single, natural-sounding paragraph. Do not use bullet points, lists, asterisks, or any special formatting.

Question: {question}
"""


def main():
    # Create CLI.
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    #parser.add_argument("--chat_history", type=str, default="[]", help="Enter chat history")
    args = parser.parse_args()
    query_text = args.query_text
    #chat_history = args.chat_history
    query_rag(query_text, [])


def query_rag(query_text: str, chat_history: list[str]):
    # Prepare the DB.
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB.
    results = db.similarity_search_with_score(query_text, k=5)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])

    # Format the chat history into a readable string.
    chat_history_text = "\n".join(chat_history)

    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, chat_history=chat_history_text, question=query_text)
    # print(prompt)

    #model = Ollama(model="llama3.1")
    model = Ollama(model="llama3")
    response_text = model.invoke(prompt)

    sources = [doc.metadata.get("id", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\n\nSources: {sources}"
    print(formatted_response)

    payload = {
        "response": response_text,
        "source": sources
    }
    #return response_text
    return payload


if __name__ == "__main__":
    main()