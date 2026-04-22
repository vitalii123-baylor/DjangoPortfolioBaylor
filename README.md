# Django Portfolio Baylor

A sophisticated Django-based financial portfolio application featuring AI-powered sentiment analysis and expense tracking, optimized for production deployment on Railway.

## Features

- **Sentiment Analyzer**: Leverages Google Gemini and custom ML models to analyze financial news and market sentiment.
- **Expense Tracker**: Intelligent tracking of financial activities with AI-assisted categorization (powered by Claude).
- **Core Portfolio**: A centralized hub showcasing projects and professional achievements.
- **Authentication**: Secure user login and signup system.

## Tech Stack

- **Backend**: Django 4.2+
- **AI/ML**: Google Gemini API, Claude API, Sentiment Analysis ML models
- **Database**: SQLite (Development) / PostgreSQL (Recommended for Production)
- **Frontend**: Django Templates, Vanilla CSS, JavaScript
- **Deployment**: Railway, Gunicorn, WhiteNoise

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/vitalii123-baylor/DjangoPortfolioBaylor.git
   cd DjangoPortfolioBaylor
   ```

2. **Setup environment**:
   - Create a virtual environment:
     ```bash
     python -m venv venv
     source venv/bin/activate  # On Windows: venv\Scripts\activate
     ```
   - Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```

3. **Database Setup**:
   ```bash
   python manage.py migrate
   ```

4. **Run the application**:
   - For development:
     ```bash
     python manage.py runserver
     ```
   - For production (using Gunicorn):
     ```bash
     gunicorn smart_finance.wsgi:application
     ```

## AI Configuration

To enable AI features, set the following environment variables:
- `GEMINI_API_KEY`: Your Google Gemini API key.
- `ANTHROPIC_API_KEY`: Your Claude API key.

## Project Structure

- `apps/core/`: Main portfolio views and home page.
- `apps/expense_tracker/`: Financial tracking logic and dashboard.
- `apps/sentiment_analyzer/`: AI-driven market sentiment analysis tools.
- `smart_finance/`: Project configuration, settings, and WSGI/ASGI entry points.
- `static/`: Static assets (CSS/JS).
- `templates/`: Global HTML templates.
- `Procfile`: Command for Railway/Heroku deployment.
- `runtime.txt`: Specifies the Python version for deployment.

## Deployment on Railway

1. Connect your GitHub repository to [Railway](https://railway.app/).
2. Railway will automatically detect the `Procfile` and `requirements.txt`.
3. Add necessary environment variables in the Railway dashboard (`GEMINI_API_KEY`, `ANTHROPIC_API_KEY`).
4. The application uses `WhiteNoise` to serve static files automatically in production.

## License

[MIT License](LICENSE)
