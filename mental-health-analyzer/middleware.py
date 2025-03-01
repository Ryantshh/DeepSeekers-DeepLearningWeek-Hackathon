import os
from functools import wraps
from flask import request, current_app

def accuracy_middleware(view_function):
    """Middleware to set accuracy level from request headers or JSON data"""
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        # Check if accuracy is specified in the request
        accuracy = None
        
        # Look for it in headers
        if 'X-Analysis-Accuracy' in request.headers:
            accuracy = request.headers.get('X-Analysis-Accuracy')
            
        # Or in JSON data
        elif request.is_json and 'accuracy' in request.get_json():
            accuracy = request.get_json().get('accuracy')
        
        # Set environment variable if accuracy is valid
        if accuracy in ['high_accuracy', 'balanced', 'fast']:
            os.environ['ANALYSIS_ACCURACY'] = accuracy
            current_app.logger.info(f"Setting analysis accuracy to {accuracy}")
        
        # Call the actual view function
        return view_function(*args, **kwargs)
        
    return decorated_function