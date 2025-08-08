# AI Conversational Voice Bot

This project is a Python-based voice assistant built on a Retrieval-Augmented Generation (RAG) framework. It uses Nomic to create text embeddings, ChromaDB as its vector store, and Llama 3.1 running locally via Ollama to generate intelligent, context-aware responses. The assistant listens for voice commands, retrieves relevant information from its knowledge base, and synthesizes speech output using Microsoft Azure's Text-to-Speech service.

## Project Structure

```
.
├── .env
├── LLM_response.json
├── Text_to_Speech.py
├── chat_brains_v2.py
├── chat_brains.py
├── config.json
├── get_embedding_function.py
├── llm_v2.py
├── requirements.txt
├── readme.md
├── stt_handler_v2.py
├── chroma/
├── data/
├── models/
└── Data_loader_v2.py

```
## Prerequisites

Before you begin, make sure you have the following installed and configured:
    - **Python 3.8+**
    - **Ollama**: You must have the Ollama application running on your system.
    - **Azure Account**: An active Azure subscription with a Speech service resource created. You'll need the API Key and Region.

## Setup and Installation

Follow these steps to get the project running.

### Step 1: Download the zip file

Download (or clone) the files to your local system

### Step 2: Set Up Ollama and Download Models

1. Download and install the Ollama application from the official website.

2. Once installed, run the application.

3. Open your terminal or command prompt and pull the necessary LLMs. This project is configured to use `llama3.1` for responses and `nomic-embed-text` for embeddings.

```
ollama pull llama3.1
ollama pull nomic-embed-text
```
Note: You can use other models, but you'll need to update the model names in the config.json and get_embedding_function.py files.

### Step 3: Create Python Environment & Install Dependencies

1. Create a Python virtual environment to keep dependencies isolated.

```
python -m venv .venv
```

2. Activate the virtual environment.

    - On Windows
    ```
    .\.venv\Scripts\activate
    ```
    - On Mac/Linux
    ```
    source .venv/bin/activate
    ```
3. Install the required Python packages from the requirements.txt file.

```
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

1. Create a file named .env in the root directory of the project.
2. Add your Azure Speech service credentials to this file. This keeps your secrets secure and out of the main codebase.

```
SPEECH_KEY="YOUR_AZURE_SPEECH_API_KEY"
SPEECH_REGION="YOUR_AZURE_SPEECH_SERVICE_REGION"
ENDPOINT="YOUR_ENDPOINT"
```

Replace the placeholder values with your actual Azure key and region.

### How to Run

With the setup complete, you can now run the main application. Make sure your Ollama application is running and your microphone is ready.

Execute the main script from your terminal:

```
python chat_brains_v2.py
```

The application will start, listen for your voice, and begin the interaction loop.

### How to load Documents

The uploader can handle `PDF` and `CSV` files. No other filetype is supported at the moment. To add the document to the RAG database, copy the document into the `data/` folder and then run `Data_loader_v2.py`
```
python Data_loader_v2.py
```
This does not need to be run every time. Run this program Only when you have new files in the `data/` folder.
