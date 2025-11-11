# Prompt Monitoring System

This document explains how to monitor prompts and responses in the CodeLingo application.

## Overview

The monitoring system automatically logs all prompts sent to OpenAI and their responses, allowing you to:
- View all prompts and responses
- Debug failed requests
- Track token usage
- Analyze prompt patterns
- Monitor API performance

## Features

### Automatic Logging
- All prompts are automatically logged to the database
- Both successful and failed requests are recorded
- Full prompts (system + user messages) are stored
- Complete responses from OpenAI are saved
- Token usage is tracked when available

### Monitoring Page
- Access via the "Monitor" link in the navigation (requires login)
- View all your prompts and responses
- Filter by operation type (generate/explain)
- Filter by language (Python/JavaScript/HTML)
- Filter by success status
- View statistics (total logs, success rate)

## Setup

### Database Migration

The `PromptLog` table will be created automatically when you start the application. If you need to create it manually:

```bash
python create_prompt_logs_table.py
```

Or restart your Flask application - it will create the table automatically.

## Usage

### Accessing the Monitor Page

1. Log in to your account
2. Click "Monitor" in the navigation bar
3. View all your prompts and responses

### Viewing Logs

Each log entry shows:
- **ID**: Unique log identifier
- **Operation Type**: Generate or Explain
- **Language**: Python, JavaScript, or HTML
- **Status**: Success or Failed
- **Timestamp**: When the prompt was sent
- **Input**: The original input (description or code)
- **Full Prompt**: Complete prompt sent to OpenAI
- **Response**: Full response from OpenAI
- **Output Code**: Generated code (for generate operations)
- **Explanation**: Explanation text
- **Tokens Used**: Number of tokens consumed
- **Model Used**: OpenAI model (e.g., gpt-3.5-turbo)

### Filtering Logs

Use the filter form to:
- Filter by operation type (generate/explain)
- Filter by programming language
- Show only successful requests
- Limit the number of results (25, 50, 100, 200)

### Console Logging

In addition to database logging, all prompts and responses are also logged to the console:
- INFO level: Successful operations
- ERROR level: Failed operations

Check your console/terminal output to see real-time logging.

## Database Schema

The `PromptLog` model includes:
- `id`: Primary key
- `user_id`: User who made the request (nullable for anonymous)
- `operation_type`: 'generate' or 'explain'
- `language`: Programming language
- `input_text`: Original input
- `full_prompt`: Complete prompt sent to OpenAI
- `response_text`: Full response from OpenAI
- `output_code`: Generated code (if applicable)
- `explanation`: Explanation text
- `success`: Boolean indicating success
- `error_message`: Error message if failed
- `tokens_used`: Number of tokens consumed
- `model_used`: OpenAI model used
- `created_at`: Timestamp

## Privacy

- Logs are user-specific: each user only sees their own logs
- Anonymous users' logs are stored but not associated with a user account
- All prompts and responses are stored in the database

## Troubleshooting

### No logs appearing?
1. Make sure you're logged in
2. Generate some code or explain some code first
3. Check that the database table was created

### Database errors?
- Ensure the database file has write permissions
- Check that SQLAlchemy can access the database
- Restart the application to recreate tables

### Missing token information?
- Token usage is only available if OpenAI includes it in the response
- Some API errors may not include token information

## Future Enhancements

Potential improvements:
- Export logs to CSV/JSON
- Search functionality
- Analytics dashboard
- Cost tracking
- Prompt templates library

