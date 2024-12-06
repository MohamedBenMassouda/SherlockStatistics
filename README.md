User Interaction and Feedback Analytics API

This project is an API designed for tracking and analyzing user interactions and feedback. The API provides endpoints for administrators to retrieve interaction statistics, manage feedback, and analyze data, as well as endpoints for authenticated users to submit feedback and create interactions.
Features
Admin Features

    Retrieve comprehensive user interaction statistics.
    Analyze user feedback by category and view recent feedback.
    Retrieve interactions for specific users with optional filtering.

User Features

    Submit feedback with ratings and categories.
    Bulk create user interactions in a single request.

# Setup
# Usage

Getting Started
Prerequisites

    Python 3.8+
    Django 4.x
    Additional dependencies in requirements.txt

Installation

    Clone the repository:

git clone <repository_url>
cd <project_directory>

Install dependencies:

pip install -r requirements.txt

Run database migrations:

python manage.py migrate

Start the development server:

    python manage.py runserver

API Documentation

The API is documented using Django REST Framework. Visit /docs for a detailed Swagger/OpenAPI documentation once the server is running.