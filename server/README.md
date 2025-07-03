# Backend Application

This is the backend application for the Gemini CLI, providing an API for chat interactions and data processing.

## Technologies Used

*   **FastAPI**: A modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints.
*   **Qdrant**: A vector similarity search engine.
*   **Sentence Transformers**: A Python framework for state-of-the-art sentence, text and image embeddings.
*   **LangChain**: A framework for developing applications powered by language models.
*   **Ollama**: A tool for running large language models locally.
*   **BeautifulSoup4**: A Python library for pulling data out of HTML and XML files.
*   **Requests**: An elegant and simple HTTP library for Python.

## Getting Started

Follow these steps to get the backend application up and running.

### Prerequisites

Make sure you have the following installed on your machine:

*   Python 3.9+
*   Poetry (for dependency management)
*   Docker (for Qdrant and Ollama)

### Installation

Navigate to the `server` directory and install the dependencies using Poetry:

```bash
cd server
poetry install
```

### Environment Variables

This application uses environment variables for configuration. Create a `.env` file in the `server` directory (where `pyproject.toml` is located) and add the following variables:

```
# server/.env
QDRANT_HOST=localhost
QDRANT_PORT=6333
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=phi4-mini
SENTENCE_TRANSFORMER_MODEL=intfloat/multilingual-e5-base
QDRANT_COLLECTION_NAME=seoul_info
MAX_CONTEXT_LENGTH=512
RESERVED_TOKENS=64
STREAM_DELAY=0.05
```

*   **`QDRANT_HOST`**: Host for Qdrant service.
*   **`QDRANT_PORT`**: Port for Qdrant service.
*   **`OLLAMA_BASE_URL`**: Base URL for your Ollama instance.
*   **`OLLAMA_MODEL`**: The Ollama model to use (e.g., `phi4-mini`).
*   **`SENTENCE_TRANSFORMER_MODEL`**: The Sentence Transformer model to use for embeddings.
*   **`QDRANT_COLLECTION_NAME`**: The name of the collection in Qdrant.
*   **`MAX_CONTEXT_LENGTH`**: Maximum token length for context truncation.
*   **`RESERVED_TOKENS`**: Reserved tokens for prompt in context truncation.
*   **`STREAM_DELAY`**: Delay in seconds for streaming responses (typing effect).

### Running Dependent Services (Qdrant & Ollama)

It is recommended to run Qdrant and Ollama using Docker. Ensure Docker is running on your system.

1.  **Start Qdrant:**

    ```bash
    docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
    ```

2.  **Start Ollama and Pull a Model (e.g., phi4-mini):**

    ```bash
    docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
    docker exec -it ollama ollama pull phi4-mini
    ```

### Data Preparation (Crawling & Embedding)

Before running the chat service, you need to crawl data and embed it into Qdrant.

1.  **Crawl Data:**

    ```bash
    cd server && poetry run python src/services/crawl_seoul.py
    ```

    This will crawl data from Wikipedia and save it to `server/data/seoul_info.txt`.

2.  **Embed Data to Qdrant:**

    ```bash
    cd server && poetry run python src/services/embed_data.py
    ```

    This will read `seoul_info.txt`, generate embeddings, and upload them to your Qdrant instance.

### Running the Backend Application

To start the FastAPI development server, run the following command from the project root directory:

```bash
cd server && poetry run uvicorn src.api.main:app --reload
```

The API will be available at `http://localhost:8000`.

## Project Structure

*   `server/src/api/`: FastAPI application entry point and API routes.
    *   `main.py`: Main FastAPI application.
*   `server/src/services/`: Business logic and interactions with external services (Qdrant, Ollama).
    *   `chat_service.py`: Handles chat logic, Qdrant search, and LLM interaction.
    *   `crawl_seoul.py`: Script for crawling data.
    *   `embed_data.py`: Script for embedding data into Qdrant.
*   `server/src/config/`: Configuration files.
    *   `settings.py`: Manages environment variables and application settings.
*   `server/data/`: Stores crawled data (e.g., `seoul_info.txt`).
