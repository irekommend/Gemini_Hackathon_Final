# Career Coaching Chatbot

**_Supercharge your career with AI-powered expert advice agent_**

This project is a web application for career coaching using a chatbot. The chatbot is designed to interact with users, provide career counseling, and answer queries related to career development. The application uses Langchain on top of the Gemini 1.5 Pro model, leveraging Langchain for ethical considerations, retrieval-augmented generation (RAG), and making the bot behave like an experienced career counselor.

## Elevator Pitch

AI-powered expert advice platform uses Google Gemini API and Claude to provide personalized, expert-level career guidance. With a 90% success rate in helping professionals achieve promotions or secure dream jobs within 6 months, our platform combines real industry expert insights with sophisticated machine learning capabilities.

Traditional career advice often falls short in the fast-paced job market. Our platform offers:

- Real-time access to expert knowledge
- Personalized AI-powered career guidance
- Data-driven insights for career progression
- 24/7 scalable coaching

### How It Works

1. **Expert Knowledge Acquisition**

   We've partnered with top industry experts who contribute through:

   - In-depth interviews
   - Panel discussions
   - Workshops
   - Mentoring sessions

   These interactions are transcribed and processed to create a comprehensive dataset of real-world career advice, strategies, and insights.

2. **Career Counselling Bot Architecture**

   - **Multi-Agent System**: The bot uses multiple agents for different tasks.
   
   - **First Agent**:
     - **Task**: Collects input from prompts.
     - **Content of Prompt**: Includes the user's resume, previous conversations, and a knowledge base (RAG).
     - **Outcome**: Generates a response based on the provided content.
       
   - **Second Agent**:
     - **Task**: Evaluates the response from the first agent.
     - **Function**: Ensures the response meets quality criteria; if not, it revises the response.
     - **Mechanism**: Uses a constitutional chain with a critique and revision process.
     - **Outcome**: Produces a refined response.
       
   - **Model Used**: Both agents utilize Gemini Pro models.

3. **Personalized Coaching Experience**

   - **Access to Elite Expertise**: Users benefit from top professionals' collective wisdom, usually inaccessible through traditional coaching.
   - **Personalization at Scale**: AI provides tailored advice to thousands of users simultaneously.
   - **24/7 Availability**: Career guidance is accessible anytime, accommodating various time zones and schedules.

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

The application is deployed on Google Cloud Run, providing a scalable and managed environment for running the chatbot.

- **Deployed URL**: [Google Cloud Run](https://gh-2wpk7qvpyq-uc.a.run.app/)
- **Domain URL**: [AI Career Coaching](https://ai.irekommend.com/)
- **Demo Video**: [YouTube Demo](https://youtu.be/2hDsRqqZwc0)

## Contact

For any questions or support, please contact:
- Arvind Radhakrishnen: arvindrkrishnen@gmail.com
- Dereck Jos: dereckjos12@gmail.com
