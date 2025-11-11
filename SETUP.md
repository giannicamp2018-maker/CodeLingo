# Setup Guide

## Quick Start

1. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create `.env` file**
   Create a file named `.env` in the root directory with the following content:
   ```
   OPENAI_API_KEY=your-openai-api-key-here
   FLASK_SECRET_KEY=your-secret-key-here
   ```

3. **Generate a secret key**
   Run this command to generate a secure secret key:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
   Copy the output and paste it as `FLASK_SECRET_KEY` in your `.env` file.

4. **Get OpenAI API Key**
   - Go to https://platform.openai.com/api-keys
   - Sign up or log in
   - Create a new API key
   - Copy the key and paste it as `OPENAI_API_KEY` in your `.env` file

5. **Run the application**
   ```bash
   python run.py
   ```

6. **Open your browser**
   Navigate to http://localhost:5000

## File Structure

```
SDET-FInal/
├── app/                    # Application code
│   ├── __init__.py        # Flask app initialization
│   ├── models.py          # Database models
│   ├── auth.py            # Authentication routes
│   ├── main.py            # Main routes
│   ├── projects.py        # Project management routes
│   ├── openai_service.py  # OpenAI API integration
│   ├── templates/         # HTML templates
│   └── static/            # CSS and JavaScript
├── instance/              # Database (created automatically)
├── config.py              # Configuration
├── requirements.txt       # Python dependencies
├── run.py                 # Application entry point
└── .env                   # Environment variables (create this)
```

## Environment Variables

Create a `.env` file in the root directory with:

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `FLASK_SECRET_KEY`: Secret key for Flask sessions (required)

## Database

The database is created automatically in the `instance/` directory when you first run the application.

## Troubleshooting

### Import Errors
- Make sure you've installed all dependencies: `pip install -r requirements.txt`
- Activate your virtual environment if you're using one

### API Key Errors
- Verify your OpenAI API key is correct in the `.env` file
- Make sure you have credits in your OpenAI account
- Check that the `.env` file is in the root directory

### Database Errors
- Make sure the `instance/` directory exists
- Check file permissions
- Try deleting the database file and restarting (this will delete all data)

### Port Already in Use
- Change the port in `run.py`: `app.run(debug=True, port=5001)`
- Or stop the process using port 5000

## Next Steps

1. Register an account
2. Create a project
3. Start generating code!

For more details, see README.md

