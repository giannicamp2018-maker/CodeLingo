"""
OpenAI API service for code generation and explanation.
Handles all interactions with the OpenAI API to generate code from descriptions
and explain existing code.
"""
import os
import logging
from openai import OpenAI
from config import Config
from app import db
from app.models import PromptLog

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client with API key from configuration
# The API key is loaded from environment variables for security
# Client is initialized lazily to avoid errors if API key is not set
_client = None

def get_client():
    """
    Get or create OpenAI client instance.
    Initializes the client with the API key from configuration.
    
    Returns:
        OpenAI client instance
    
    Raises:
        ValueError: If API key is not configured
    """
    global _client
    # Always get fresh API key from config (in case .env was updated)
    api_key = Config.OPENAI_API_KEY
    if not api_key:
        raise ValueError("OpenAI API key is not configured. Please set OPENAI_API_KEY in your .env file.")
    
    # Reinitialize client if API key changed or client doesn't exist
    if _client is None or getattr(_client, '_api_key', None) != api_key:
        _client = OpenAI(api_key=api_key)
        # Store API key for comparison
        _client._api_key = api_key
    
    return _client


def reset_client():
    """
    Reset the OpenAI client instance.
    Useful when API key is updated and needs to be reloaded.
    """
    global _client
    _client = None


def generate_code_from_description(language, description, user_id=None):
    """
    Generate code from an English description using OpenAI API.
    
    Args:
        language: Programming language ('python', 'javascript', or 'html')
        description: English description of what the code should do
        user_id: Optional user ID for logging purposes
    
    Returns:
        Dictionary with 'code' and 'explanation' keys, or None if error occurs
    
    Raises:
        Exception: If OpenAI API call fails
    """
    # Log the prompt being sent
    logger.info(f"Generating {language} code from description: {description[:100]}...")
    
    try:
        # Create a detailed prompt for code generation
        # The prompt instructs the AI to generate well-commented, educational code
        prompt = f"""Generate {language} code based on the following description: {description}

Requirements:
1. Write clean, well-structured code that accomplishes the task
2. Include detailed comments explaining what each section of the code does
3. Use best practices for the {language} language
4. Make the code educational and easy to understand for students learning to program

After the code, provide a detailed explanation of:
- What the code does overall
- How each major part works
- Key programming concepts used
- Any important patterns or techniques

Format your response as:
CODE:
[your code here]

EXPLANATION:
[your explanation here]"""

        # Get OpenAI client - this will raise ValueError if API key is not configured
        try:
            client = get_client()
        except ValueError as e:
            # API key not configured
            return {
                'code': None,
                'explanation': str(e),
                'success': False
            }
        
        # Prepare messages for API call
        system_message = f"You are a helpful programming tutor that generates {language} code with detailed explanations."
        user_message = prompt
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        # Log the full prompt
        full_prompt_text = f"System: {system_message}\n\nUser: {user_message}"
        logger.info(f"Full prompt:\n{full_prompt_text}")
        
        # Call OpenAI API to generate code
        # Using gpt-3.5-turbo model for cost-effectiveness and good quality
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,  # Slightly creative but focused
            max_tokens=2000  # Limit response length
        )
        
        # Extract the response text
        response_text = response.choices[0].message.content
        
        # Extract token usage if available
        tokens_used = None
        if hasattr(response, 'usage') and response.usage:
            tokens_used = getattr(response.usage, 'total_tokens', None)
        
        # Log the response
        logger.info(f"Response received ({len(response_text)} chars, {tokens_used} tokens): {response_text[:200]}...")
        
        # Parse the response to separate code and explanation
        # Strategy 1: Look for "CODE:" and "EXPLANATION:" markers
        if "CODE:" in response_text and "EXPLANATION:" in response_text:
            parts = response_text.split("EXPLANATION:")
            code_part = parts[0].replace("CODE:", "").strip()
            explanation_part = parts[1].strip()
        # Strategy 2: Look for markdown code blocks (between ```)
        elif "```" in response_text:
            code_blocks = response_text.split("```")
            # Find the code block (usually has language identifier)
            code_part = ""
            explanation_part = ""
            
            # Look for code blocks with language identifiers
            for i in range(1, len(code_blocks), 2):
                if i < len(code_blocks):
                    block = code_blocks[i].strip()
                    # Remove language identifier if present
                    if block.startswith(language) or block.startswith('python') or block.startswith('javascript') or block.startswith('html') or block.startswith('css'):
                        lines = block.split('\n', 1)
                        if len(lines) > 1:
                            code_part = lines[1].strip()
                        else:
                            code_part = block
                    elif not code_part:  # Use first code block if no language match
                        code_part = block.split('\n', 1)[-1].strip() if '\n' in block else block.strip()
            
            # Everything after the code blocks is explanation
            if len(code_blocks) > 2:
                explanation_part = code_blocks[-1].strip()
            else:
                explanation_part = "See code above for implementation."
            
            # If no code found, try using the first block
            if not code_part and len(code_blocks) >= 3:
                code_part = code_blocks[1].split('\n', 1)[-1].strip() if '\n' in code_blocks[1] else code_blocks[1].strip()
        else:
            # Strategy 3: Try to find code-like patterns or use entire response
            # Check if response looks like code (contains common programming keywords)
            code_keywords = ['def ', 'function ', 'class ', 'import ', 'const ', 'let ', '<html', '<div', '<?php']
            if any(keyword in response_text for keyword in code_keywords):
                # Assume entire response is code
                code_part = response_text
                explanation_part = "This code implements the requested functionality."
            else:
                # Assume entire response is explanation with embedded code
                code_part = response_text
                explanation_part = "See code above for details."
        
        # Log to database
        try:
            log_entry = PromptLog(
                user_id=user_id,
                operation_type='generate',
                language=language,
                input_text=description,
                full_prompt=full_prompt_text,
                response_text=response_text,
                output_code=code_part,
                explanation=explanation_part,
                success=True,
                tokens_used=tokens_used,
                model_used='gpt-3.5-turbo'
            )
            db.session.add(log_entry)
            db.session.commit()
            logger.info(f"Prompt logged to database with ID: {log_entry.id}")
        except Exception as log_error:
            logger.error(f"Failed to log prompt to database: {str(log_error)}")
            db.session.rollback()
        
        # Return code and explanation
        return {
            'code': code_part,
            'explanation': explanation_part,
            'success': True
        }
    
    except Exception as e:
        # Handle all OpenAI API errors
        error_details = str(e)
        error_message = "An error occurred with the OpenAI API."
        
        # Log full error for debugging
        print(f"Full error details: {type(e).__name__}: {error_details}")
        if hasattr(e, '__dict__'):
            print(f"Error attributes: {e.__dict__}")
        
        # Try to extract error response if available
        error_body = None
        error_type = None
        status_code = None
        
        # Check if it's an OpenAI API error with response
        if hasattr(e, 'response'):
            try:
                if hasattr(e.response, 'status_code'):
                    status_code = e.response.status_code
                if hasattr(e.response, 'json'):
                    error_body = e.response.json()
                    if isinstance(error_body, dict):
                        error_info = error_body.get('error', {})
                        if isinstance(error_info, dict):
                            error_type = error_info.get('type', '')
                            error_code = error_info.get('code', '')
                            error_msg = error_info.get('message', '')
                            print(f"Error type: {error_type}, code: {error_code}, message: {error_msg}")
            except Exception as parse_error:
                print(f"Could not parse error response: {parse_error}")
        
        # Parse error message to detect specific error types
        error_lower = error_details.lower()
        
        # Check for connection errors
        if 'connection' in error_lower or 'connect' in error_lower or 'network' in error_lower:
            error_message = (
                "⚠️ Connection Error\n\n"
                "Unable to connect to OpenAI API. Please check your internet connection and try again."
            )
        # Check for timeout errors
        elif 'timeout' in error_lower or 'timed out' in error_lower:
            error_message = (
                "⚠️ Request Timeout\n\n"
                "The request to OpenAI API timed out. Please try again."
            )
        # Check for 429 errors - need to distinguish between rate limit and quota
        elif status_code == 429 or '429' in error_details:
            # Check if it's specifically an insufficient_quota error
            if error_type == 'insufficient_quota' or 'insufficient_quota' in error_lower:
                error_message = (
                    "⚠️ OpenAI API Quota Exceeded\n\n"
                    "Your OpenAI account has exceeded its quota or has no available credits. "
                    "To fix this:\n\n"
                    "1. Check your OpenAI account billing: https://platform.openai.com/account/billing\n"
                    "2. Verify your API key belongs to the account with the balance\n"
                    "3. Check if there are any spending limits set on your account\n"
                    "4. Ensure your payment method is valid and up to date\n\n"
                    "Note: If you just added credits, it may take a few minutes to process.\n\n"
                    f"Error details: {error_details}\n\n"
                    "For more information, visit: https://platform.openai.com/docs/guides/error-codes"
                )
            else:
                # This is a rate limit, not a quota issue
                error_message = (
                    "⚠️ Rate Limit Exceeded\n\n"
                    "You're making requests too quickly. Please wait a moment and try again.\n\n"
                    "Rate limits are separate from your account balance. Even with credits, "
                    "OpenAI enforces rate limits to ensure fair usage.\n\n"
                    "If this persists, you may need to:\n"
                    "1. Wait a few minutes before trying again\n"
                    "2. Reduce the frequency of your requests\n"
                    "3. Check your rate limits: https://platform.openai.com/account/limits\n\n"
                    f"Error details: {error_details}"
                )
        # Check for authentication errors (401)
        elif status_code == 401 or '401' in error_details or 'unauthorized' in error_lower or 'invalid api key' in error_lower:
            error_message = (
                "⚠️ Invalid API Key\n\n"
                "Your OpenAI API key is invalid or not configured correctly.\n\n"
                "Please verify:\n"
                "1. The API key in your .env file is correct\n"
                "2. The API key hasn't been revoked\n"
                "3. You've restarted the application after updating the .env file\n"
                "4. The API key belongs to the account with the balance\n\n"
                f"Error details: {error_details}"
            )
        # Check for permission errors (403)
        elif status_code == 403 or '403' in error_details or 'forbidden' in error_lower or 'permission' in error_lower:
            error_message = (
                "⚠️ Access Forbidden\n\n"
                "Your API key doesn't have permission to access this resource. "
                "Please check your OpenAI account permissions and API key configuration."
            )
        # Generic API error
        else:
            # Include more details in the error message
            error_message = (
                f"⚠️ OpenAI API Error\n\n"
                f"Error: {error_details}\n\n"
                "Please check:\n"
                "1. Your API key is correct and active\n"
                "2. Your account has sufficient credits\n"
                "3. Your internet connection is working\n"
                "4. The OpenAI API service is available\n\n"
                "For more information, visit: https://platform.openai.com/docs/guides/error-codes"
            )
        
        logger.error(f"Error generating code: {error_message}")
        
        # Log error to database
        try:
            log_entry = PromptLog(
                user_id=user_id,
                operation_type='generate',
                language=language,
                input_text=description,
                full_prompt=full_prompt_text if 'full_prompt_text' in locals() else prompt,
                response_text=None,
                success=False,
                error_message=error_message,
                model_used='gpt-3.5-turbo'
            )
            db.session.add(log_entry)
            db.session.commit()
        except Exception as log_error:
            logger.error(f"Failed to log error to database: {str(log_error)}")
            db.session.rollback()
        
        print(f"Error generating code: {error_message}")
        return {
            'code': None,
            'explanation': error_message,
            'error': error_message,
            'success': False
        }


def explain_code(language, code, user_id=None):
    """
    Explain what a piece of code does using OpenAI API.
    
    Args:
        language: Programming language ('python', 'javascript', or 'html')
        code: The code to explain
        user_id: Optional user ID for logging purposes
    
    Returns:
        Dictionary with 'explanation' key, or None if error occurs
    
    Raises:
        Exception: If OpenAI API call fails
    """
    # Log the prompt being sent
    logger.info(f"Explaining {language} code ({len(code)} chars): {code[:100]}...")
    
    try:
        # Create a detailed prompt for code explanation
        # The prompt instructs the AI to provide educational, comprehensive explanations
        prompt = f"""Explain the following {language} code in detail. Break down what the code does, how it works, and explain key programming concepts.

Code:
{code}

Provide an explanation that:
1. Describes what the code does overall
2. Explains each major section or function
3. Identifies key programming concepts used
4. Explains any important patterns, algorithms, or techniques
5. Is educational and helpful for students learning to program

Make the explanation clear, detailed, and easy to understand."""

        # Get OpenAI client - this will raise ValueError if API key is not configured
        try:
            client = get_client()
        except ValueError as e:
            # API key not configured
            return {
                'explanation': str(e),
                'success': False
            }
        
        # Prepare messages for API call
        system_message = f"You are a helpful programming tutor that explains {language} code in detail. Keep the explination short and concise, and do not include any other text than the explanation."
        user_message = prompt
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        # Log the full prompt
        full_prompt_text = f"System: {system_message}\n\nUser: {user_message}"
        logger.info(f"Full prompt:\n{full_prompt_text}")
        
        # Call OpenAI API to explain the code
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.5,  # More focused for explanations
            max_tokens=1500  # Limit response length
        )
        
        # Extract the explanation text
        explanation = response.choices[0].message.content
        
        # Extract token usage if available
        tokens_used = None
        if hasattr(response, 'usage') and response.usage:
            tokens_used = getattr(response.usage, 'total_tokens', None)
        
        # Log the response
        logger.info(f"Response received ({len(explanation)} chars, {tokens_used} tokens): {explanation[:200]}...")
        
        # Log to database
        try:
            log_entry = PromptLog(
                user_id=user_id,
                operation_type='explain',
                language=language,
                input_text=code,
                full_prompt=full_prompt_text,
                response_text=explanation,
                output_code=None,
                explanation=explanation,
                success=True,
                tokens_used=tokens_used,
                model_used='gpt-3.5-turbo'
            )
            db.session.add(log_entry)
            db.session.commit()
            logger.info(f"Prompt logged to database with ID: {log_entry.id}")
        except Exception as log_error:
            logger.error(f"Failed to log prompt to database: {str(log_error)}")
            db.session.rollback()
        
        # Return explanation
        return {
            'explanation': explanation,
            'success': True
        }
    
    except Exception as e:
        # Handle all OpenAI API errors (same logic as generate_code_from_description)
        error_details = str(e)
        error_message = "An error occurred with the OpenAI API."
        
        # Log full error for debugging
        print(f"Full error details: {type(e).__name__}: {error_details}")
        if hasattr(e, '__dict__'):
            print(f"Error attributes: {e.__dict__}")
        
        # Try to extract error response if available
        error_body = None
        error_type = None
        status_code = None
        
        # Check if it's an OpenAI API error with response
        if hasattr(e, 'response'):
            try:
                if hasattr(e.response, 'status_code'):
                    status_code = e.response.status_code
                if hasattr(e.response, 'json'):
                    error_body = e.response.json()
                    if isinstance(error_body, dict):
                        error_info = error_body.get('error', {})
                        if isinstance(error_info, dict):
                            error_type = error_info.get('type', '')
                            error_code = error_info.get('code', '')
                            error_msg = error_info.get('message', '')
                            print(f"Error type: {error_type}, code: {error_code}, message: {error_msg}")
            except Exception as parse_error:
                print(f"Could not parse error response: {parse_error}")
        
        # Parse error message to detect specific error types
        error_lower = error_details.lower()
        
        # Check for connection errors
        if 'connection' in error_lower or 'connect' in error_lower or 'network' in error_lower:
            error_message = (
                "⚠️ Connection Error\n\n"
                "Unable to connect to OpenAI API. Please check your internet connection and try again."
            )
        # Check for timeout errors
        elif 'timeout' in error_lower or 'timed out' in error_lower:
            error_message = (
                "⚠️ Request Timeout\n\n"
                "The request to OpenAI API timed out. Please try again."
            )
        # Check for 429 errors - need to distinguish between rate limit and quota
        elif status_code == 429 or '429' in error_details:
            # Check if it's specifically an insufficient_quota error
            if error_type == 'insufficient_quota' or 'insufficient_quota' in error_lower:
                error_message = (
                    "⚠️ OpenAI API Quota Exceeded\n\n"
                    "Your OpenAI account has exceeded its quota or has no available credits. "
                    "To fix this:\n\n"
                    "1. Check your OpenAI account billing: https://platform.openai.com/account/billing\n"
                    "2. Verify your API key belongs to the account with the balance\n"
                    "3. Check if there are any spending limits set on your account\n"
                    "4. Ensure your payment method is valid and up to date\n\n"
                    "Note: If you just added credits, it may take a few minutes to process.\n\n"
                    f"Error details: {error_details}\n\n"
                    "For more information, visit: https://platform.openai.com/docs/guides/error-codes"
                )
            else:
                # This is a rate limit, not a quota issue
                error_message = (
                    "⚠️ Rate Limit Exceeded\n\n"
                    "You're making requests too quickly. Please wait a moment and try again.\n\n"
                    "Rate limits are separate from your account balance. Even with credits, "
                    "OpenAI enforces rate limits to ensure fair usage.\n\n"
                    "If this persists, you may need to:\n"
                    "1. Wait a few minutes before trying again\n"
                    "2. Reduce the frequency of your requests\n"
                    "3. Check your rate limits: https://platform.openai.com/account/limits\n\n"
                    f"Error details: {error_details}"
                )
        # Check for authentication errors (401)
        elif status_code == 401 or '401' in error_details or 'unauthorized' in error_lower or 'invalid api key' in error_lower:
            error_message = (
                "⚠️ Invalid API Key\n\n"
                "Your OpenAI API key is invalid or not configured correctly.\n\n"
                "Please verify:\n"
                "1. The API key in your .env file is correct\n"
                "2. The API key hasn't been revoked\n"
                "3. You've restarted the application after updating the .env file\n"
                "4. The API key belongs to the account with the balance\n\n"
                f"Error details: {error_details}"
            )
        # Check for permission errors (403)
        elif status_code == 403 or '403' in error_details or 'forbidden' in error_lower or 'permission' in error_lower:
            error_message = (
                "⚠️ Access Forbidden\n\n"
                "Your API key doesn't have permission to access this resource. "
                "Please check your OpenAI account permissions and API key configuration."
            )
        # Generic API error
        else:
            # Include more details in the error message
            error_message = (
                f"⚠️ OpenAI API Error\n\n"
                f"Error: {error_details}\n\n"
                "Please check:\n"
                "1. Your API key is correct and active\n"
                "2. Your account has sufficient credits\n"
                "3. Your internet connection is working\n"
                "4. The OpenAI API service is available\n\n"
                "For more information, visit: https://platform.openai.com/docs/guides/error-codes"
            )
        
        logger.error(f"Error explaining code: {error_message}")
        
        # Log error to database
        try:
            log_entry = PromptLog(
                user_id=user_id,
                operation_type='explain',
                language=language,
                input_text=code,
                full_prompt=full_prompt_text if 'full_prompt_text' in locals() else prompt,
                response_text=None,
                success=False,
                error_message=error_message,
                model_used='gpt-3.5-turbo'
            )
            db.session.add(log_entry)
            db.session.commit()
        except Exception as log_error:
            logger.error(f"Failed to log error to database: {str(log_error)}")
            db.session.rollback()
        
        print(f"Error explaining code: {error_message}")
        return {
            'explanation': error_message,
            'error': error_message,
            'success': False
        }

