# Programming Learning Platform

A web application that helps students learn programming by generating code from English descriptions and explaining existing code. Built with Flask (Python backend) and modern web technologies.

## Deployment

**Try it now:** [https://codelingo-rouge.vercel.app/](https://codelingo-rouge.vercel.app/)

## Features

- **Code Generation**: Enter an English description and get code in Python, C++, JavaScript, CSS, HTML, or Java
- **Code Explanation**: Paste code and get a detailed explanation of how it works
- **User Authentication**: Secure user registration and login with password hashing
- **Project Management**: Create projects/folders to organize your code examples
- **Save Examples**: Save generated code and explanations to projects for later reference
- **Dark Theme**: Modern dark monochrome theme with dark green accents

## Prerequisites

- Python 3.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- pip (Python package manager)

## Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd SDET-FInal
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**
   - Copy `.env.example` to `.env` (if it exists) or create a new `.env` file
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=your-api-key-here
     FLASK_SECRET_KEY=your-secret-key-here
     ```
   - Generate a secret key for Flask sessions:
     ```bash
     python -c "import secrets; print(secrets.token_hex(32))"
     ```

6. **Initialize the database**
   - The database will be created automatically when you run the application
   - It will be stored in the `instance/` directory

## Running the Application

1. **Make sure your virtual environment is activated**

2. **Run the application**
   ```bash
   python run.py
   ```

3. **Open your browser**
   - Navigate to `http://localhost:5000`
   - The application should be running!

## Usage

### Getting Started

1. **Register an account**
   - Click "Register" in the navigation bar
   - Fill in your username, email, and password
   - Click "Register" to create your account

2. **Login**
   - Click "Login" and enter your credentials
   - You'll be redirected to the home page

3. **Create a project**
   - Click "My Projects" in the navigation bar
   - Enter a project name and click "Create Project"
   - Projects help you organize your code examples

### Generating Code

1. **Select a language**
   - Click on the Python, C++, JavaScript, CSS, HTML, or Java tab

2. **Choose mode**
   - "Description → Code": Enter what you want the code to do in English
   - "Code → Explanation": Paste code you want explained

3. **Enter your input**
   - For code generation: Describe what you want in English
   - For code explanation: Paste your code

4. **Select a project (optional)**
   - If you're logged in, select a project to save the result

5. **Click the button**
   - "Generate Code" or "Explain Code"
   - Wait for the AI to process your request

6. **View results**
   - Generated code will be displayed with syntax highlighting
   - Explanation will appear below the code
   - You can copy the code to clipboard

### Managing Projects

1. **View projects**
   - Click "My Projects" in the navigation bar
   - See all your projects and when they were created

2. **View project details**
   - Click "View" on any project
   - See all saved code examples in that project
   - Filter by language or type

3. **Delete projects**
   - Click "Delete" on any project
   - Confirm deletion (this will delete all saved prompts in the project)

## Project Structure

```
SDET-FInal/
├── app/
│   ├── __init__.py              # Flask app initialization
│   ├── models.py                # Database models
│   ├── auth.py                  # Authentication routes
│   ├── main.py                  # Main application routes
│   ├── projects.py              # Project management routes
│   ├── openai_service.py        # OpenAI API integration
│   ├── templates/               # HTML templates
│   └── static/                  # CSS and JavaScript files
├── instance/                    # Database file (created automatically)
├── config.py                    # Configuration settings
├── requirements.txt             # Python dependencies
├── run.py                       # Application entry point
└── README.md                    # This file
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `FLASK_SECRET_KEY`: Secret key for Flask sessions (required for production)
- `DATABASE_URL`: Database connection URL (optional, defaults to SQLite)

### Database

- The application uses SQLite by default
- Database file is stored in `instance/database.db`
- Tables are created automatically on first run

## Security Features

- Password hashing using Werkzeug
- SQL injection protection (SQLAlchemy ORM)
- XSS protection (Jinja2 auto-escaping)
- Session management
- Input validation

## Troubleshooting

### Common Issues

1. **OpenAI API Error**
   - Make sure your API key is correct in the `.env` file
   - Check that you have credits in your OpenAI account
   - Verify your internet connection

2. **Database Error**
   - Make sure the `instance/` directory exists
   - Check file permissions
   - Try deleting the database file and restarting (this will delete all data)

3. **Import Errors**
   - Make sure all dependencies are installed: `pip install -r requirements.txt`
   - Verify your virtual environment is activated

4. **Port Already in Use**
   - Change the port in `run.py`: `app.run(debug=True, port=5001)`
   - Or stop the process using port 5000

## Development

### Adding New Features

1. **New Routes**: Add to appropriate blueprint file (`auth.py`, `main.py`, `projects.py`)
2. **New Models**: Add to `app/models.py`
3. **New Templates**: Add to `app/templates/`
4. **New Styles**: Add to `app/static/css/style.css`
5. **New JavaScript**: Add to `app/static/js/main.js` or inline in templates

### Code Style

- Follow PEP 8 for Python code
- Use descriptive variable and function names
- Add comments explaining complex logic
- Keep functions focused on a single task

## License

This project is for educational purposes.

## Support

For issues or questions, please check the troubleshooting section or review the code comments for guidance.

## Acknowledgments

- Flask framework for web application framework
- OpenAI for AI-powered code generation and explanation
- SQLAlchemy for database ORM
- Werkzeug for password hashing and security


