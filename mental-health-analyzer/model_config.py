import os

def get_model_config():
    """Return optimized model configuration based on analysis needs."""
    
    # Define model options based on accuracy needs
    model_options = {
        "high_accuracy": {
            "model": "llama3-70b-8192",  # Use the larger model for more accurate analysis
            "temperature": 0.1,          # Keep temperature low for consistency
            "max_tokens": 3000,          # Allow for more detailed analysis
            "top_p": 0.95,               # Slightly restrict token selection
            "frequency_penalty": 0.1,    # Slight penalty to avoid repetition
            "presence_penalty": 0.1      # Slight penalty to encourage coverage of all topics
        },
        "balanced": {
            "model": "llama3-8b-8192",   # Default model
            "temperature": 0.2,          # Slightly higher temperature
            "max_tokens": 2000,
            "top_p": 0.9,
            "frequency_penalty": 0,
            "presence_penalty": 0
        },
        "fast": {
            "model": "llama3-8b-8192",
            "temperature": 0.3,
            "max_tokens": 1500,
            "top_p": 0.85,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }
    }
    
    # Always use high accuracy
    accuracy_level = "high_accuracy"
    
    # Override with environment variables if specified
    config = model_options[accuracy_level]
    
    if os.getenv("GROQ_MODEL"):
        config["model"] = os.getenv("GROQ_MODEL")
    
    return config