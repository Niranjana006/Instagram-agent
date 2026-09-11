# Influencer Agent

An autonomous AI-powered Instagram Influencer Assistant that helps creators manage their presence, generate content, and interact with followers.

## Features

- **AI-Powered Content Generation:** Upload an image and let the agent analyze its visuals using Google's Gemini Vision API. It will automatically generate tailored captions and relevant hashtags.
- **Style Learning:** The agent learns the creator's unique voice and writing style based on past Instagram posts, ensuring that all generated content sounds authentic.
- **Content Planning:** Automatically generates weekly structured content plans based on the creator's niche and style profile.
- **Optimal Time Prediction:** Recommends the best times to post based on engagement history.
- **Automated Webhooks:** Listens to Instagram webhooks (via Facebook Graph API) for real-time interactions.

## Tech Stack

- **Backend:** FastAPI (Python)
- **AI Integration:** Google Gemini API (`gemini-2.5-flash` for text and vision)
- **Database:** PostgreSQL (with SQLAlchemy)
- **Background Tasks:** Celery + Redis (for scheduling and async processing)
- **Instagram API:** Facebook Graph API Integration

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Niranjana006/Instagram-agent.git
   cd Instagram-agent
   ```

2. **Set up the virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Environment Variables:**
   Create a `.env` file in the root directory and add the following keys:
   ```env
   GEMINI_API_KEY=your_gemini_key
   INSTAGRAM_ACCESS_TOKEN=your_instagram_token
   INSTAGRAM_ACCOUNT_ID=your_account_id
   INSTAGRAM_APP_ID=your_app_id
   INSTAGRAM_APP_SECRET=your_app_secret
   WEBHOOK_VERIFY_TOKEN=your_custom_webhook_secret

   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=your_db_password
   POSTGRES_SERVER=localhost
   POSTGRES_DB=influencer_agent
   DATABASE_URL=postgresql://postgres:your_db_password@localhost:5432/influencer_agent

   CELERY_BROKER_URL=redis://localhost:6379/0
   CELERY_RESULT_BACKEND=redis://localhost:6379/0
   ```

4. **Run the Application:**

   **Start the Database and Redis (Docker recommended):**
   ```bash
   docker-compose -f infra/docker-compose.yml up -d
   ```

   **Start the FastAPI server:**
   ```bash
   uvicorn app.main:app --reload
   ```

   **Start the Celery worker (in a separate terminal):**
   ```bash
   celery -A worker.celery_app worker --loglevel=info
   ```

## Getting the Long-Lived Instagram Token

Run the included token helper script to easily generate and exchange short-lived tokens for long-lived ones:
```bash
python get_token.py
```
