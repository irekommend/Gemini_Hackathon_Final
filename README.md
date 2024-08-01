# Career Coaching Chatbot

This project is a web application for career coaching using a chatbot. The chatbot is designed to interact with users, provide career counseling, and answer queries related to career development. The application uses Langchain on top of the Gemini 1.5 Pro model, leveraging Langchain for ethical considerations, retrieval-augmented generation (RAG), and making the bot behave like an experienced career counselor.

## Features
- User Registration and Login
- Resume Upload for Career Coaching
- Interactive Career Counseling Chatbot
- Ethical Response Filtering using Langchain's Constitutional Layer
- Retrieval-Augmented Generation (RAG) using MongoDB Atlas Vector Database
  
## Installation and Setup

### Prerequisites

- Python 3.9+
- Docker (for containerized deployment)

### Local Setup

1. **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/career-coaching-chatbot.git
    cd career-coaching-chatbot
    ```

2. **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Run the application:**
    ```bash
    python app.py
    ```

### Docker Setup

1. **Build the Docker image:**
    ```bash
    docker build -t career-coaching-chatbot .
    ```

2. **Run the Docker container:**
    ```bash
    docker run -p 815:815 career-coaching-chatbot
    ```

## Application Flow

1. **Register to Career Coaching:**
   - Users need to register on the platform to access the career coaching services.

2. **Login:**
   - After registration, users can log in to their accounts.

3. **Upload Resume:**
   - Users can upload their resumes for personalized career coaching and counseling.

4. **Interact with the Bot:**
   - Users can interact with the chatbot, ask questions regarding career counseling, and receive responses.

## Technical Overview

### Langchain and Gemini 1.5 Pro Integration

- **Langchain**: Used for its Constitutional Layer to ensure ethical responses, and for implementing RAG (Retrieval-Augmented Generation). Langchain helps in adding ethical considerations to the responses, ensuring the bot behaves like a career counselor.

- **Gemini 1.5 Pro Model**: Provides the core capabilities for answering career-related queries. The model is accessed via API.

### Query Flow

1. **User Query**: The user's question/query is captured.

2. **Vector Database Search**: The query is passed to the MongoDB Atlas Vector Database. Using Euclidean Distance Metric, relevant documents are retrieved.

3. **Prompt Construction**: The retrieved documents, along with the user's query and resume content, are used to construct a prompt.

4. **LLM Response**: The prompt is sent to the Gemini 1.5 Pro model, which generates a response.

5. **Constitutional Chain**: The response is passed through Langchain's Constitutional Chain to ensure it is ethical and contextually appropriate.

6. **Conversation Continuity**: Langchain also helps maintain the continuity of the conversation by memorizing previous interactions.

### Deployment on Google Cloud Run

The application is deployed on Google Cloud Run, providing a scalable and managed environment for running the chatbot. The deployed link is: [https://gh-2wpk7qvpyq-uc.a.run.app/](https://gh-2wpk7qvpyq-uc.a.run.app/).

## Contact
For any questions or support, please contact:
- Arvind Radhakrishnen: arvindrkrishnen@gmail.com
- Dereck Jos: dereckjos12@gmail.com
