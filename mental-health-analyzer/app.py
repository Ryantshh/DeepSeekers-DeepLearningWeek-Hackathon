from flask import Flask, render_template, request, jsonify
import requests
import json
import os
import logging
import traceback
import re
from dotenv import load_dotenv
from datetime import datetime
# Add this at the beginning with other imports
from therapist_routes import register_therapist_routes
from flask_cors import CORS

# Add this after app initialization
# Register therapist routes


# Import our custom modules
from text_processing import preprocess_text
from model_config import get_model_config
from clinical_validation import validate_clinical_assessment

# Load environment variables
load_dotenv()

app = Flask(__name__)
register_therapist_routes(app)
CORS(app)
# Configure Groq API
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192")  # Default to Llama 3 8B model

# Define the DSM-5 Level 1 Cross-Cutting Symptom Measure domains and questions
DSM5_DOMAINS = [
    {
        "name": "Depression",
        "questions": [
            "Little interest or pleasure in doing things",
            "Feeling down, depressed, or hopeless"
        ],
        "max_score": 8,  # 2 questions × 4 (max per question)
        "threshold": 2,
        "color": "#8A2BE2"  # BlueViolet
    },
    {
        "name": "Anger",
        "questions": [
            "Feeling more irritated, grouchy, or angry than usual"
        ],
        "max_score": 4,  # 1 question × 4 (max per question)
        "threshold": 2,
        "color": "#FF4500"  # OrangeRed
    },
    {
        "name": "Mania",
        "questions": [
            "Sleeping less than usual, but still have a lot of energy",
            "Starting lots more projects than usual or doing more risky things than usual"
        ],
        "max_score": 8,  # 2 questions × 4 (max per question)
        "threshold": 2,
        "color": "#FF8C00"  # DarkOrange
    },
    {
        "name": "Anxiety",
        "questions": [
            "Feeling nervous, anxious, frightened, worried, or on edge",
            "Feeling panic or being frightened",
            "Avoiding situations that make you anxious"
        ],
        "max_score": 12,  # 3 questions × 4 (max per question)
        "threshold": 2,
        "color": "#4682B4"  # SteelBlue
    },
    {
        "name": "Somatic Symptoms",
        "questions": [
            "Unexplained aches and pains",
            "Feeling that your illnesses are not being taken seriously enough"
        ],
        "max_score": 8,  # 2 questions × 4 (max per question)
        "threshold": 2,
        "color": "#2E8B57"  # SeaGreen
    },
    {
        "name": "Suicidal Ideation",
        "questions": [
            "Thoughts of actually hurting yourself"
        ],
        "max_score": 4,  # 1 question × 4 (max per question)
        "threshold": 1,  # Lower threshold for suicidal ideation
        "color": "#B22222"  # FireBrick
    },
    {
        "name": "Psychosis",
        "questions": [
            "Hearing things other people couldn't hear, such as voices",
            "Feeling that someone could hear your thoughts, or that you could hear what another person was thinking"
        ],
        "max_score": 8,  # 2 questions × 4 (max per question)
        "threshold": 1,  # Lower threshold for psychosis
        "color": "#9932CC"  # DarkOrchid
    },
    {
        "name": "Sleep Problems",
        "questions": [
            "Problems with sleep that affected your sleep quality"
        ],
        "max_score": 4,  # 1 question × 4 (max per question)
        "threshold": 2,
        "color": "#6495ED"  # CornflowerBlue
    },
    {
        "name": "Memory",
        "questions": [
            "Problems with memory"
        ],
        "max_score": 4,  # 1 question × 4 (max per question)
        "threshold": 2,
        "color": "#3CB371"  # MediumSeaGreen
    },
    {
        "name": "Repetitive Thoughts and Behaviors",
        "questions": [
            "Unpleasant thoughts, urges, or images that repeatedly enter your mind",
            "Feeling driven to perform certain behaviors or mental acts over and over again"
        ],
        "max_score": 8,  # 2 questions × 4 (max per question)
        "threshold": 2,
        "color": "#DAA520"  # GoldenRod
    },
    {
        "name": "Dissociation",
        "questions": [
            "Feeling detached or distant from yourself, your body, your physical surroundings, or your memories"
        ],
        "max_score": 4,  # 1 question × 4 (max per question)
        "threshold": 2,
        "color": "#9370DB"  # MediumPurple
    },
    {
        "name": "Personality Functioning",
        "questions": [
            "Not knowing who you really are or what you want out of life",
            "Not feeling close to other people or enjoying relationships"
        ],
        "max_score": 8,  # 2 questions × 4 (max per question)
        "threshold": 2,
        "color": "#4169E1"  # RoyalBlue
    },
    {
        "name": "Substance Use",
        "questions": [
            "Drinking at least 4 drinks of any kind of alcohol in a single day",
            "Smoking any cigarettes, a cigar, or pipe, or using snuff or chewing tobacco",
            "Using any of the following medicines on your own: pain medications, stimulants, sedatives or tranquilizers, or drugs like marijuana, cocaine or crack, club drugs, hallucinogens, heroin, inhalants, or methamphetamine"
        ],
        "max_score": 12,  # 3 questions × 4 (max per question)
        "threshold": 1,  # Lower threshold for substance use
        "color": "#808000"  # Olive
    }
]

# Severity interpretation guide
SEVERITY_LEVELS = [
    {"range": [0, 0], "label": "None", "color": "#28a745"},
    {"range": [1, 1], "label": "Slight/Rare", "color": "#17a2b8"},
    {"range": [2, 2], "label": "Mild", "color": "#ffc107"},
    {"range": [3, 3], "label": "Moderate", "color": "#fd7e14"},
    {"range": [4, 4], "label": "Severe", "color": "#dc3545"}
]

def configure_logging():
    """Configure logging for the application"""
    if not app.debug:
        # In production, log to file
        file_handler = logging.FileHandler('app.log')
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)
    else:
        # In development, log to console with more details
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        stream_handler.setFormatter(formatter)
        app.logger.addHandler(stream_handler)
        app.logger.setLevel(logging.INFO)

# Configure logging
configure_logging()



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    try:
        # Analyze the text
        result = analyze_text(text)
        
        # Create directory for saving results
        results_dir = os.path.join(os.getcwd(), 'analysis_results')
        os.makedirs(results_dir, exist_ok=True)
        
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mental_health_analysis_{timestamp}.json"
        file_path = os.path.join(results_dir, filename)
        
        # Prepare JSON data to save
        json_save_data = {
            "domains": [
                {
                    "name": domain["name"],
                    "scores": domain["scores"],
                    "evidence": domain["evidence"],
                    "total": domain["total"],
                    "risk_percentage": domain.get("risk_percentage", 0),
                    "severity": domain.get("severity", "None"),
                    "clinical_concern": domain.get("clinical_concern", False)
                } for domain in result.get("domains", [])
            ],
            "summary": result.get("summary", {})
        }
        
        # Save the file
        with open(file_path, 'w') as f:
            json.dump(json_save_data, f, indent=2)
        
        # Return the analysis result
        return jsonify(result)
    
    except Exception as e:
        # Error handling
        error_details = traceback.format_exc()
        app.logger.error(f"Error during analysis: {str(e)}\n{error_details}")
        
        return jsonify({
            "error": "Analysis failed",
            "details": str(e)
        }), 500
def analyze_text(text):
    """Enhanced text analysis using DSM-5 Level 1 Cross-Cutting Symptom Measure with Groq API"""
    
    if not GROQ_API_KEY:
        raise Exception("Groq API key is missing. Please set the GROQ_API_KEY environment variable.")
    
    # Use enhanced preprocessing
    processed_text = preprocess_text(text)
    app.logger.info(f"Preprocessed text length: {len(processed_text)}")
    
    # Get optimal model configuration
    model_config = get_model_config()
    app.logger.info(f"Using model: {model_config['model']} with temperature: {model_config.get('temperature', 0.1)}")
    
    # Create improved system prompt
    system_prompt = """
    You are a specialized mental health analysis assistant trained specifically on the DSM-5 Level 1 Cross-Cutting Symptom Measure (Adult Version).

    SCORING GUIDELINES:
    0: None - No evidence at all of the symptom
    1: Slight/Rare - Very minimal evidence, mentioned in passing, or a single isolated instance
    2: Mild/Several days - Clear but infrequent or low-intensity evidence appearing in multiple contexts
    3: Moderate/More than half the days - Strong evidence appearing consistently or with moderate intensity
    4: Severe/Nearly every day - Overwhelming evidence or explicit statements about severe and frequent symptoms

    IMPORTANT SCORING RULES:
    - Use the FULL RANGE of scores from 0-4 based on the evidence severity
    - Do NOT limit scores to 2 or below - use 3 and 4 when evidence supports it
    - Provide specific quotes that justify each score, with context
    - Consider frequency, intensity, duration, and distress when scoring
    - Look for patterns across the entire text rather than isolated mentions
    - If a symptom is explicitly denied, score it as 0
    - When you see clear evidence of moderate (3) or severe (4) symptoms, score accordingly

    EXAMPLES OF HIGHER SCORES (3-4):
    - For score 3 (Moderate): Evidence shows symptoms occur "more than half the days" or with "significant intensity"
    - For score 4 (Severe): Evidence shows symptoms are "nearly constant" or "overwhelming" or "severely impairing"

    Your analysis must be evidence-based, objective, clinically meaningful, and use the FULL SCORING RANGE.
    Format your response as a JSON object with no additional explanation.
    """
    
    # Create the user prompt with all domains and questions
    user_prompt = f"""
    Text to analyze: 

    {processed_text}
    
    Please analyze the above text and complete the DSM-5 Level 1 Cross-Cutting Symptom Measure:
    
    """
    
    # Add all domains and questions to the prompt
    domain_question_index = 1
    for domain_index, domain in enumerate(DSM5_DOMAINS):
        user_prompt += f"\nDomain {domain_index + 1}. {domain['name']}:\n"
        for question_index, question in enumerate(domain['questions']):
            user_prompt += f"{domain_question_index}. {question}\n"
            domain_question_index += 1
    
    user_prompt += """
    EXAMPLES OF PROPER SCORING:
    
    Example 1: "I've been having trouble sleeping the past couple weeks. I wake up around 3am most nights."
    Score: 3 (Moderate/More than half the days)
    Evidence: "I wake up around 3am most nights."
    Rationale: The phrase "most nights" indicates frequency of more than half the days.
    
    Example 2: "Sometimes I get a bit nervous before presentations."
    Score: 1 (Slight/Rare)
    Evidence: "Sometimes I get a bit nervous before presentations."
    Rationale: "Sometimes" and "a bit" indicate low frequency and intensity.
    
    Example 3: "I can't focus on anything. My mind is constantly racing with worry about everything."
    Score: 4 (Severe/Nearly every day)
    Evidence: "I can't focus on anything. My mind is constantly racing with worry about everything."
    Rationale: "Constantly" indicates very high frequency, and "can't focus on anything" suggests severity.
    
    Remember to quote specific text as evidence for each score you assign.
    
    Respond with only a JSON object in this exact format:
    {
      "domains": [
        {
          "name": "Domain name",
          "scores": [score1, score2, ...],
          "evidence": ["Direct quote from text as evidence for score 1", "Direct quote from text as evidence for score 2", ...],
          "total": totalScore
        },
        ... (repeat for all domains)
      ]
    }
    """
    
    # Configure headers for the API request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }
    
    # Prepare the payload for Groq API
    payload = {
        "model": model_config["model"],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": model_config.get("temperature", 0.1),
        "max_tokens": model_config.get("max_tokens", 2000),
        "top_p": model_config.get("top_p", 0.95),
        "frequency_penalty": model_config.get("frequency_penalty", 0),
        "presence_penalty": model_config.get("presence_penalty", 0),
        "response_format": {"type": "json_object"}
    }
    
    try:
        # Make the API request to Groq
        app.logger.info(f"Sending request to Groq API")
        response = requests.post(
            GROQ_API_URL,
            headers=headers,
            json=payload,
            timeout=90  # Extended timeout for more complex analysis
        )
        
        # Check for successful response
        if response.status_code != 200:
            error_msg = f"API request failed with status code {response.status_code}: {response.text}"
            app.logger.error(error_msg)
            raise Exception(error_msg)
        
        # Parse the response
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        # Try to parse the response as JSON
        try:
            parsed_result = json.loads(content)
        except json.JSONDecodeError:
            # If that fails, try to extract JSON using regex
            app.logger.warning("JSON parsing failed, attempting to extract JSON from text")
            json_match = re.search(r'({.*})', content, re.DOTALL)
            if json_match:
                try:
                    parsed_result = json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    error_msg = "Failed to extract valid JSON from the model response"
                    app.logger.error(f"{error_msg}: {content}")
                    raise Exception(error_msg)
            else:
                error_msg = "No JSON object found in the model response"
                app.logger.error(f"{error_msg}: {content}")
                raise Exception(error_msg)
        
        # Validate the structure of the parsed result
        if "domains" not in parsed_result:
            error_msg = "Response is missing required domains field"
            app.logger.error(f"{error_msg}: {parsed_result}")
            raise Exception(error_msg)
        
        # Process and validate each domain
        validated_domains = []
        for i, domain_data in enumerate(parsed_result.get("domains", [])):
            # Map domain to our defined domains
            if i >= len(DSM5_DOMAINS):
                app.logger.warning(f"Extra domain in response: {domain_data.get('name', 'Unknown')}")
                continue
            
            domain = DSM5_DOMAINS[i]
            
            # Ensure all required fields exist with valid values
            if "name" not in domain_data or domain_data["name"] != domain["name"]:
                domain_data["name"] = domain["name"]
                
            # Validate scores array 
            if "scores" not in domain_data or not isinstance(domain_data["scores"], list):
                domain_data["scores"] = [0] * len(domain["questions"])
            else:
                # Ensure correct length
                while len(domain_data["scores"]) < len(domain["questions"]):
                    domain_data["scores"].append(0)
                domain_data["scores"] = domain_data["scores"][:len(domain["questions"])]
                
                # Validate each score (ensure full range 0-4 is allowed)
                for s_idx, score in enumerate(domain_data["scores"]):
                    if not isinstance(score, (int, float)) or score < 0 or score > 4:
                        app.logger.warning(f"Invalid score in domain {domain['name']}, question {s_idx+1}: {score}")
                        domain_data["scores"][s_idx] = 0
                    else:
                        # Ensure score is an integer between 0-4 (no capping below maximum)
                        domain_data["scores"][s_idx] = min(4, max(0, int(score)))
            
            # Validate evidence array
            if "evidence" not in domain_data or not isinstance(domain_data["evidence"], list):
                domain_data["evidence"] = ["No explicit evidence found in the text."] * len(domain["questions"])
            else:
                # Ensure correct length
                while len(domain_data["evidence"]) < len(domain["questions"]):
                    domain_data["evidence"].append("No explicit evidence found in the text.")
                domain_data["evidence"] = domain_data["evidence"][:len(domain["questions"])]
                
                # Validate each evidence string
                for e_idx, evidence in enumerate(domain_data["evidence"]):
                    if not isinstance(evidence, str) or not evidence.strip():
                        domain_data["evidence"][e_idx] = "No explicit evidence found in the text."
            
            # Calculate total score
            domain_data["total"] = sum(domain_data["scores"])
            
            # Calculate risk percentage
            risk_percentage = round((domain_data["total"] / domain["max_score"] * 100), 1)
            domain_data["risk_percentage"] = risk_percentage
            
            # Determine severity based on highest individual question score
            max_score = max(domain_data["scores"]) if domain_data["scores"] else 0
            severity = None
            for level in SEVERITY_LEVELS:
                if max_score >= level["range"][0] and max_score <= level["range"][1]:
                    severity = level
            
            # If no severity was found, use "None" level
            if severity is None:
                severity = SEVERITY_LEVELS[0]
            
            # Determine if this domain is clinically concerning
            clinical_concern = max_score >= domain["threshold"]
            
            # Add these to the domain data
            domain_data["severity"] = severity["label"]
            domain_data["severity_color"] = severity["color"]
            domain_data["domain_color"] = domain["color"]
            domain_data["clinical_concern"] = clinical_concern
            domain_data["questions"] = domain["questions"]
            domain_data["threshold"] = domain["threshold"]
            
            validated_domains.append(domain_data)
        
        # Fill in any missing domains
        while len(validated_domains) < len(DSM5_DOMAINS):
            i = len(validated_domains)
            domain = DSM5_DOMAINS[i]
            empty_domain = {
                "name": domain["name"],
                "scores": [0] * len(domain["questions"]),
                "evidence": ["No data received from analysis."] * len(domain["questions"]),
                "total": 0,
                "risk_percentage": 0,
                "severity": SEVERITY_LEVELS[0]["label"],
                "severity_color": SEVERITY_LEVELS[0]["color"],
                "domain_color": domain["color"],
                "clinical_concern": False,
                "questions": domain["questions"],
                "threshold": domain["threshold"]
            }
            validated_domains.append(empty_domain)
        
        # Apply clinical validation logic
        validated_domains = validate_clinical_assessment(validated_domains)
        
        # Prepare the final output
        return {
            "domains": validated_domains,
            "summary": {
                "clinical_concerns": [
                    domain["name"] for domain in validated_domains 
                    if domain.get("clinical_concern", False)
                ],
                "confidence_levels": {
                    domain["name"]: domain.get("confidence", "Medium") 
                    for domain in validated_domains
                },
                "notes": [
                    f"{domain['name']}: {', '.join(domain['clinical_notes'])}" 
                    for domain in validated_domains
                    if domain.get('clinical_notes')
                ]
            }
        }
        
    except requests.RequestException as e:
        error_msg = f"Network error contacting Groq API: {str(e)}"
        app.logger.error(error_msg)
        raise Exception(error_msg)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)