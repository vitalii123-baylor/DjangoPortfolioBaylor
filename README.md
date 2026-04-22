# Django Portfolio Baylor

A sophisticated Django-based financial portfolio application featuring AI-powered sentiment analysis and expense tracking.

## Features

- **Sentiment Analyzer**: Leverages Google Gemini and custom ML models to analyze financial news and market sentiment.
- **Expense Tracker**: Intelligent tracking of financial activities with AI-assisted categorization.
- **Core Portfolio**: A centralized hub showcasing projects and professional achievements.
- **Authentication**: Secure user login and signup system.

## Tech Stack

- **Backend**: Django 4.x, Python 3.x
- **AI/ML**: Google Gemini API, Claude API, Sentiment Analysis ML models
- **Database**: SQLite (default)
- **Frontend**: Django Templates, Vanilla CSS, JavaScript

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
     pip install -r smart_finance/requirements.txt
     ```

3. **Database Setup**:
   ```bash
   python smart_finance/manage.py migrate
   ```

4. **Run the application**:
   - Using the provided batch file (Windows):
     ```bash
     cd smart_finance
     run.bat
     ```
   - Or via Python:
     ```bash
     python smart_finance/manage.py runserver
     ```

## AI Configuration

To enable AI features, you need to provide API keys for Gemini and Claude in your environment settings (or a `.env` file).

## Project Structure

- `apps/core/`: Main portfolio views and home page.
- `apps/expense_tracker/`: Financial tracking logic and dashboard.
- `apps/sentiment_analyzer/`: AI-driven market sentiment analysis tools.
- `smart_finance/`: Project configuration and settings.

## License

[MIT License](LICENSE)
