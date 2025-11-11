"""
OpenAI API service for code generation and explanation.
Handles all interactions with the OpenAI API to generate code from descriptions
and explain existing code.
"""
import os
from openai import OpenAI
from config import Config

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
    if _client is None:
        api_key = Config.OPENAI_API_KEY
        if not api_key:
            raise ValueError("OpenAI API key is not configured. Please set OPENAI_API_KEY in your .env file.")
        _client = OpenAI(api_key=api_key)
    return _client


def generate_code_from_description(language, description):
    """
    Generate code from an English description using OpenAI API.
    
    Args:
        language: Programming language ('python', 'javascript', or 'html')
        description: English description of what the code should do
    
    Returns:
        Dictionary with 'code' and 'explanation' keys, or None if error occurs
    
    Raises:
        Exception: If OpenAI API call fails
    """
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
        
        # Call OpenAI API to generate code
        # Using gpt-3.5-turbo model for cost-effectiveness and good quality
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a helpful programming tutor that generates {language} code with detailed explanations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,  # Slightly creative but focused
            max_tokens=2000  # Limit response length
        )
        
        # Extract the response text
        response_text = response.choices[0].message.content
        
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
        
        # Return code and explanation
        return {
            'code': code_part,
            'explanation': explanation_part,
            'success': True
        }
    
    except Exception as e:
        # Handle errors (API failures, network issues, etc.)
        print(f"Error generating code: {str(e)}")
        return {
            'code': None,
            'explanation': f"Error generating code: {str(e)}. Please check your API key and try again.",
            'success': False
        }


def explain_code(language, code):
    """
    Explain what a piece of code does using OpenAI API.
    
    Args:
        language: Programming language ('python', 'javascript', or 'html')
        code: The code to explain
    
    Returns:
        Dictionary with 'explanation' key, or None if error occurs
    
    Raises:
        Exception: If OpenAI API call fails
    """
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
        
        # Call OpenAI API to explain the code
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a helpful programming tutor that explains {language} code in detail."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,  # More focused for explanations
            max_tokens=1500  # Limit response length
        )
        
        # Extract the explanation text
        explanation = response.choices[0].message.content
        
        # Return explanation
        return {
            'explanation': explanation,
            'success': True
        }
    
    except Exception as e:
        # Handle errors (API failures, network issues, etc.)
        print(f"Error explaining code: {str(e)}")
        return {
            'explanation': f"Error explaining code: {str(e)}. Please check your API key and try again.",
            'success': False
        }

