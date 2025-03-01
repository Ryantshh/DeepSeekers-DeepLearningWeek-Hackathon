# Import necessary modules
import os
import json
import re
import traceback
import logging
from datetime import datetime
from flask import render_template, request, jsonify
import requests
from text_processing import preprocess_text

# Define DSM-5 Level 2 assessment tools mapping
DSM5_LEVEL2_TOOLS = {
    "Depression": {
        "name": "PHQ-9 (Patient Health Questionnaire-9)",
        "description": "A 9-item depression scale to assist clinicians with diagnosing depression and monitoring treatment response.",
        "max_score": 27,
        "threshold": 10,
        "questions": [
            "Little interest or pleasure in doing things",
            "Feeling down, depressed, or hopeless",
            "Trouble falling/staying asleep, sleeping too much",
            "Feeling tired or having little energy",
            "Poor appetite or overeating",
            "Feeling bad about yourself or that you're a failure or have let yourself or your family down",
            "Trouble concentrating on things, such as reading the newspaper or watching television",
            "Moving or speaking so slowly that other people could have noticed, or the opposite—being so fidgety or restless that you have been moving around a lot more than usual",
            "Thoughts that you would be better off dead or of hurting yourself in some way"
        ],
        "scoring": [
            {"range": [0, 4], "level": "None to minimal depression", "description": "Monitor; may not require treatment"},
            {"range": [5, 9], "level": "Mild depression", "description": "Watchful waiting; consider counseling, follow-up"},
            {"range": [10, 14], "level": "Moderate depression", "description": "Treatment plan, counseling, follow-up"},
            {"range": [15, 19], "level": "Moderately severe depression", "description": "Active treatment with pharmacotherapy and/or psychotherapy"},
            {"range": [20, 27], "level": "Severe depression", "description": "Immediate initiation of pharmacotherapy and, if severe impairment or poor response to therapy, expedited referral to a mental health specialist"}
        ]
    },
    "Anxiety": {
        "name": "GAD-7 (Generalized Anxiety Disorder-7)",
        "description": "A 7-item anxiety scale to screen for and measure the severity of generalized anxiety disorder.",
        "max_score": 21,
        "threshold": 10,
        "questions": [
            "Feeling nervous, anxious, or on edge",
            "Not being able to stop or control worrying",
            "Worrying too much about different things",
            "Trouble relaxing",
            "Being so restless that it's hard to sit still",
            "Becoming easily annoyed or irritable",
            "Feeling afraid as if something awful might happen"
        ],
        "scoring": [
            {"range": [0, 4], "level": "Minimal anxiety", "description": "May not require treatment"},
            {"range": [5, 9], "level": "Mild anxiety", "description": "Watchful waiting, follow-up"},
            {"range": [10, 14], "level": "Moderate anxiety", "description": "Possible clinically significant condition; consider counseling"},
            {"range": [15, 21], "level": "Severe anxiety", "description": "Active treatment with pharmacotherapy and/or psychotherapy"}
        ]
    },
    "Suicidal Ideation": {
        "name": "C-SSRS (Columbia-Suicide Severity Rating Scale)",
        "description": "A tool that helps identify whether someone is at risk for suicide.",
        "max_score": 25,
        "threshold": 6,
        "questions": [
            "Have you wished you were dead or wished you could go to sleep and not wake up?",
            "Have you actually had any thoughts about killing yourself?",
            "Have you thought about how you might kill yourself?",
            "Have you had any intention of acting on these thoughts?",
            "Have you started to work out or worked out the details of how to kill yourself? Do you intend to carry out this plan?"
        ],
        "scoring": [
            {"range": [0, 5], "level": "Low risk", "description": "Continue monitoring, safety planning if appropriate"},
            {"range": [6, 15], "level": "Moderate risk", "description": "Safety planning, increased monitoring, consider referral"},
            {"range": [16, 25], "level": "High risk", "description": "Immediate intervention required, safety planning, possible hospitalization"}
        ]
    },
    "Anger": {
        "name": "PROMIS Anger",
        "description": "A measure for evaluating anger in adults.",
        "max_score": 40,
        "threshold": 27,
        "questions": [
            "I felt angry",
            "I felt like I was ready to explode",
            "I was grouchy",
            "I felt annoyed",
            "I felt like I needed to let out my anger",
            "I had trouble controlling my temper",
            "I felt like yelling at someone",
            "I felt like breaking things"
        ],
        "scoring": [
            {"range": [0, 13], "level": "Low anger", "description": "Minimal concern; continue monitoring"},
            {"range": [14, 26], "level": "Moderate anger", "description": "Consider anger management strategies"},
            {"range": [27, 40], "level": "High anger", "description": "Significant concern; intervention recommended"}
        ]
    },
    "Mania": {
        "name": "Altman Self-Rating Mania Scale (ASRM)",
        "description": "A 5-item self-rating mania scale to assess the presence and severity of manic symptoms.",
        "max_score": 20,
        "threshold": 6,
        "questions": [
            "Elevated/Euphoric Mood: Happiness, optimism, self-confidence",
            "Increased Motor Activity/Energy: More energy, more active, more restless",
            "Sexual Interest: More sexual interest, more sexual thoughts, sexual activity",
            "Sleep: Less need for sleep than usual",
            "Irritability: More irritable, more argumentative, less tolerant"
        ],
        "scoring": [
            {"range": [0, 5], "level": "No indication of mania", "description": "Continue monitoring if clinical suspicion exists"},
            {"range": [6, 10], "level": "Possible hypomania", "description": "Further assessment recommended; consider mood stabilization strategies"},
            {"range": [11, 20], "level": "High probability of mania", "description": "Immediate psychiatric evaluation recommended"}
        ]
    },
    "Somatic Symptoms": {
        "name": "PHQ-15 (Patient Health Questionnaire-15)",
        "description": "A 15-item somatic symptom scale to screen for somatization and to monitor somatic symptom severity.",
        "max_score": 30,
        "threshold": 10,
        "questions": [
            "Stomach pain",
            "Back pain",
            "Pain in your arms, legs, or joints",
            "Menstrual cramps or other problems with your periods (women only)",
            "Headaches",
            "Chest pain",
            "Dizziness",
            "Fainting spells",
            "Feeling your heart pound or race",
            "Shortness of breath",
            "Pain or problems during sexual intercourse",
            "Constipation, loose bowels, or diarrhea",
            "Nausea, gas, or indigestion",
            "Feeling tired or having low energy",
            "Trouble sleeping"
        ],
        "scoring": [
            {"range": [0, 4], "level": "Minimal somatic symptoms", "description": "Normal range; no intervention needed"},
            {"range": [5, 9], "level": "Low somatic symptoms", "description": "Monitor symptoms; consider physical evaluation if persistent"},
            {"range": [10, 14], "level": "Medium somatic symptoms", "description": "Consider comprehensive evaluation for physical and psychological factors"},
            {"range": [15, 30], "level": "High somatic symptoms", "description": "Significant somatization likely; comprehensive treatment plan recommended"}
        ]
    },
    "Psychosis": {
        "name": "PRIME Screen-Revised",
        "description": "A 12-item self-report screen designed to identify individuals who may be experiencing early signs of psychosis.",
        "max_score": 24,
        "threshold": 7,
        "questions": [
            "I think that I have felt that there are odd or unusual things going on that I can't explain.",
            "I think that I might be able to predict the future.",
            "I may have felt that there could possibly be something interrupting or controlling my thoughts, feelings, or actions.",
            "I have had the experience of doing something differently because of my superstitions.",
            "I think that I may get confused at times whether something I experience or perceive may be real or may be just part of my imagination or dreams.",
            "I have thought that it might be possible that other people can read my mind, or that I can read others' minds."
        ],
        "scoring": [
            {"range": [0, 6], "level": "Low likelihood of psychosis risk", "description": "Continue monitoring if concerns persist"},
            {"range": [7, 13], "level": "Possible psychosis risk", "description": "Further specialized assessment recommended"},
            {"range": [14, 24], "level": "High likelihood of psychosis risk", "description": "Prompt psychiatric evaluation recommended"}
        ]
    },
    "Sleep Problems": {
        "name": "ISI (Insomnia Severity Index)",
        "description": "A 7-item self-report questionnaire assessing the nature, severity, and impact of insomnia.",
        "max_score": 28,
        "threshold": 15,
        "questions": [
            "Difficulty falling asleep",
            "Difficulty staying asleep",
            "Problems waking up too early",
            "How satisfied/dissatisfied are you with your current sleep pattern?",
            "How noticeable to others do you think your sleep problem is in terms of impairing the quality of your life?",
            "How worried/distressed are you about your current sleep problem?",
            "To what extent do you consider your sleep problem to interfere with your daily functioning currently?"
        ],
        "scoring": [
            {"range": [0, 7], "level": "No clinically significant insomnia", "description": "No intervention needed"},
            {"range": [8, 14], "level": "Subthreshold insomnia", "description": "Sleep hygiene education may be helpful"},
            {"range": [15, 21], "level": "Moderate clinical insomnia", "description": "Treatment indicated; sleep hygiene, cognitive-behavioral therapy"},
            {"range": [22, 28], "level": "Severe clinical insomnia", "description": "Severe insomnia requiring comprehensive treatment approach"}
        ]
    },
    "Memory": {
        "name": "PROMIS Cognitive Function",
        "description": "A measure of perceived cognitive abilities.",
        "max_score": 40,
        "threshold": 14,
        "questions": [
            "I have had to work harder than usual to keep track of what I was doing",
            "I have had trouble shifting back and forth between different activities that require thinking",
            "My thinking has been slow",
            "I have had trouble forming thoughts",
            "I have had trouble adding or subtracting numbers in my head",
            "I have had trouble figuring out what I meant to do once I got there",
            "I have had trouble finding my way to a familiar place",
            "I have had trouble concentrating"
        ],
        "scoring": [
            {"range": [0, 13], "level": "Severe cognitive concerns", "description": "Comprehensive neuropsychological evaluation recommended"},
            {"range": [14, 26], "level": "Moderate cognitive concerns", "description": "Further assessment recommended; consider cognitive interventions"},
            {"range": [27, 40], "level": "Minimal cognitive concerns", "description": "Monitor if symptoms persist"}
        ]
    },
    "Repetitive Thoughts and Behaviors": {
        "name": "FOCI (Florida Obsessive-Compulsive Inventory)",
        "description": "A self-report measure of obsessive-compulsive symptoms.",
        "max_score": 20,
        "threshold": 8,
        "questions": [
            "Time occupied by obsessive thoughts",
            "Interference from obsessive thoughts",
            "Distress from obsessive thoughts",
            "Resistance to obsessive thoughts",
            "Control over obsessive thoughts",
            "Time spent performing compulsive behaviors",
            "Interference from compulsive behaviors",
            "Distress from compulsive behaviors",
            "Resistance to compulsive behaviors",
            "Control over compulsive behaviors"
        ],
        "scoring": [
            {"range": [0, 7], "level": "Minimal OCD symptoms", "description": "Monitor if symptoms persist"},
            {"range": [8, 13], "level": "Moderate OCD symptoms", "description": "Further assessment and possible intervention recommended"},
            {"range": [14, 20], "level": "Severe OCD symptoms", "description": "Specialized OCD treatment recommended"}
        ]
    },
    "Dissociation": {
        "name": "DES-II (Dissociative Experiences Scale)",
        "description": "A 28-item self-report measure of dissociative symptoms.",
        "max_score": 40,
        "threshold": 20,
        "questions": [
            "Some people have the experience of finding themselves in a place and having no idea how they got there.",
            "Some people have the experience of finding themselves dressed in clothes that they don't remember putting on.",
            "Some people have the experience of finding new things among their belongings that they do not remember buying.",
            "Some people sometimes find that they are approached by people that they do not know who call them by another name or insist that they have met them before.",
            "Some people have the experience of feeling as though they are standing next to themselves or watching themselves do something and they actually see themselves as if they were looking at another person."
        ],
        "scoring": [
            {"range": [0, 10], "level": "Normal range", "description": "No clinical concern"},
            {"range": [11, 20], "level": "Mild dissociation", "description": "Monitor for exacerbation; consider addressing triggers"},
            {"range": [21, 30], "level": "Moderate dissociation", "description": "Clinical intervention recommended; trauma-focused therapy may be beneficial"},
            {"range": [31, 40], "level": "Severe dissociation", "description": "Comprehensive trauma-focused treatment recommended"}
        ]
    },
    "Personality Functioning": {
        "name": "PID-5 (Personality Inventory for DSM-5)",
        "description": "A self-rated personality trait assessment scale for adults.",
        "max_score": 40,
        "threshold": 14,
        "questions": [
            "I don't get as much pleasure out of things as others seem to.",
            "I feel like I act totally on impulse.",
            "I often have thoughts that make sense to me but that other people say are strange.",
            "I avoid risky situations.",
            "It's no big deal if I hurt other people's feelings.",
            "I rarely get enthusiastic about anything.",
            "I go out of my way to avoid any kind of conflict.",
            "I'm inflexible in my ways, even when it would clearly be to my advantage to change."
        ],
        "scoring": [
            {"range": [0, 13], "level": "Low personality dysfunction", "description": "Minimal clinical concern"},
            {"range": [14, 26], "level": "Moderate personality dysfunction", "description": "Further assessment and possible intervention recommended"},
            {"range": [27, 40], "level": "High personality dysfunction", "description": "Comprehensive personality assessment and treatment recommended"}
        ]
    },
    "Substance Use": {
        "name": "ASSIST (Alcohol, Smoking and Substance Involvement Screening Test)",
        "description": "A screening test to assess use of psychoactive substances.",
        "max_score": 39,
        "threshold": 11,
        "questions": [
            "In your life, which of the following substances have you ever used?",
            "In the past three months, how often have you used the substances you mentioned?",
            "In the past three months, how often have you had a strong desire or urge to use?",
            "In the past three months, how often has your use of substances led to health, social, legal, or financial problems?",
            "In the past three months, how often have you failed to do what was normally expected of you because of your use of substances?",
            "Has a friend or relative or anyone else ever expressed concern about your use of substances?",
            "Have you ever tried and failed to control, cut down or stop using substances?"
        ],
        "scoring": [
            {"range": [0, 10], "level": "Low risk", "description": "General education on substance use"},
            {"range": [11, 26], "level": "Moderate risk", "description": "Brief intervention and monitoring recommended"},
            {"range": [27, 39], "level": "High risk", "description": "Intensive assessment and treatment recommended"}
        ]
    }
}

def register_therapist_routes(app):
    """Register therapist dashboard routes with the Flask app"""
    
    @app.route('/therapist')
    def therapist_dashboard():
        """Render the therapist dashboard page"""
        return render_template('therapist_dashboard.html')
    
    @app.route('/api/assessment-files')
    def get_assessment_files():
        """Get list of assessment result files"""
        try:
            results_dir = os.path.join(os.getcwd(), 'analysis_results')
            if not os.path.exists(results_dir):
                return jsonify({'files': []})
            
            files = [f for f in os.listdir(results_dir) if f.endswith('.json')]
            files.sort(reverse=True)  # Most recent first
            
            return jsonify({'files': files})
        except Exception as e:
            app.logger.error(f"Error getting assessment files: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/assessment-data')
    def get_assessment_data():
        """Get data from a specific assessment file"""
        try:
            file = request.args.get('file')
            if not file:
                return jsonify({'error': 'No file specified'}), 400
            
            file_path = os.path.join(os.getcwd(), 'analysis_results', file)
            if not os.path.exists(file_path):
                return jsonify({'error': 'File not found'}), 404
            
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            return jsonify(data)
        except Exception as e:
            app.logger.error(f"Error getting assessment data: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/therapy-sessions')
    def get_therapy_sessions():
        """Get list of therapy session files"""
        try:
            # For demonstration, we'll create a sessions directory if it doesn't exist
            sessions_dir = os.path.join(os.getcwd(), 'therapy_sessions')
            os.makedirs(sessions_dir, exist_ok=True)
            
            
            files = [f for f in os.listdir(sessions_dir) if f.endswith('.txt')]
            files.sort(reverse=True)  # Most recent first
            
            return jsonify({'files': files})
        except Exception as e:
            app.logger.error(f"Error getting therapy sessions: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/therapy-session')
    def get_therapy_session():
        """Get content of a specific therapy session file"""
        try:
            file = request.args.get('file')
            if not file:
                return jsonify({'error': 'No file specified'}), 400
            
            file_path = os.path.join(os.getcwd(), 'therapy_sessions', file)
            if not os.path.exists(file_path):
                return jsonify({'error': 'File not found'}), 404
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            return jsonify({'content': content})
        except Exception as e:
            app.logger.error(f"Error getting therapy session: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/run-assessment', methods=['POST'])
    def run_assessment():
        """Run a Level 2 assessment on a therapy session"""
        try:
            data = request.get_json()
            domain = data.get('domain')
            session_file = data.get('session')
            
            if not domain or not session_file:
                return jsonify({'error': 'Domain and session file required'}), 400
            
            # Get domain tool
            tool = DSM5_LEVEL2_TOOLS.get(domain)
            if not tool:
                return jsonify({'error': f'No assessment tool found for domain: {domain}'}), 400
            
            # Get session content
            file_path = os.path.join(os.getcwd(), 'therapy_sessions', session_file)
            if not os.path.exists(file_path):
                return jsonify({'error': 'Session file not found'}), 404
            
            with open(file_path, 'r') as f:
                session_content = f.read()
            
            # Preprocess session content
            processed_content = preprocess_text(session_content)
            
            # Call Groq API to analyze the session
            try:
                assessment_result = analyze_session_with_groq(processed_content, domain, tool, app)
                
                # Verify the result structure before returning
                if not assessment_result or 'scores' not in assessment_result or not isinstance(assessment_result['scores'], list):
                    app.logger.error(f"Invalid assessment result structure: {assessment_result}")
                    return jsonify({
                        'error': 'Invalid assessment result structure from LLM',
                        'details': 'The model response did not match the expected format.'
                    }), 500
                    
                return jsonify(assessment_result)
            except Exception as e:
                app.logger.error(f"Error from LLM processing: {str(e)}")
                # Return a more detailed error response
                return jsonify({
                    'error': f'Error analyzing session: {str(e)}',
                    'details': traceback.format_exc()
                }), 500
                
        except Exception as e:
            app.logger.error(f"Error running assessment: {str(e)}")
            # Return a formatted error response
            return jsonify({
                'error': str(e),
                'details': traceback.format_exc()
            }), 500


def analyze_session_with_groq(session_content, domain, tool, app):
    """Analyze a therapy session using Groq API for a specific domain"""
    # Get API key from environment variable
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise Exception("Groq API key is missing. Please set the GROQ_API_KEY environment variable.")
    
    api_url = "https://api.groq.com/openai/v1/chat/completions"
    model = os.environ.get("GROQ_MODEL", "llama3-8b-8192")
    
    # Create system prompt
    system_prompt = f"""
    You are a specialized mental health assessment assistant trained on the {tool['name']}.
    You will carefully analyze therapy session text to identify evidence of symptoms related to {domain}.
    
    SCORING GUIDELINES:
    0: None - No evidence at all of the symptom
    1: Slight/Rare - Very minimal evidence, mentioned in passing, or a single isolated instance
    2: Mild/Several days - Clear but infrequent or low-intensity evidence appearing in multiple contexts
    3: Moderate/More than half the days - Strong evidence appearing consistently or with moderate intensity
    4: Severe/Nearly every day - Overwhelming evidence or explicit statements about severe and frequent symptoms
    
    IMPORTANT SCORING RULES:
    - Use the FULL RANGE of scores from 0-4 based on the evidence severity
    - Provide specific quotes from the session text that justify each score
    - Consider frequency, intensity, duration, and distress when scoring
    - If a symptom is explicitly denied, score it as 0
    
    Format your response as a JSON object with no additional explanation.
    """
    
    # Create user prompt with EXPLICIT formatting instructions
    user_prompt = f"""
    Therapy session text to analyze: 

    {session_content}
    
    Please analyze the above therapy session transcript and complete the {tool['name']} for {domain}:
    
    """
    
    # Add all questions to the prompt
    for i, question in enumerate(tool['questions']):
        user_prompt += f"\n{i+1}. {question}"
    
    user_prompt += """
    
    IMPORTANT: Your response must be valid JSON with no annotations within the strings.
    
    Respond with ONLY this exact JSON format:
    {
      "scores": [score1, score2, ...],
      "evidence": ["Direct quote from text", "Direct quote from text", ...]
    }
    
    For evidence, include ONLY the direct quotes without any annotations, explanations, or score indicators in parentheses.
    For example, use "I feel sad" NOT "I feel sad (score 2)".
    
    If no evidence is found for a question, use "No specific evidence found in the session." as the evidence string.
    """
    
    # Configure headers for the API request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # Prepare the payload for Groq API
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 2000,
        "top_p": 0.95,
        "response_format": {"type": "json_object"}
    }
    
    # Make the API request
    response = requests.post(
        api_url,
        headers=headers,
        json=payload,
        timeout=90
    )
    
    # Log API response
    app.logger.info(f"Received response from Groq API with status: {response.status_code}")
    
    # Check for successful response
    if response.status_code != 200:
        raise Exception(f"API request failed with status code {response.status_code}: {response.text}")
    
    # Parse the response
    result = response.json()
    content = result["choices"][0]["message"]["content"]
    
    # Log parsed content
    app.logger.info(f"Parsed API response content: {content[:500]}...")
    
    # Try to parse the response as JSON
    try:
        assessment_result = json.loads(content)
    except json.JSONDecodeError:
        # If that fails, try to extract JSON using regex
        json_match = re.search(r'({.*})', content, re.DOTALL)
        if json_match:
            try:
                assessment_result = json.loads(json_match.group(1))
            except json.JSONDecodeError:
                raise Exception("Failed to extract valid JSON from the model response")
        else:
            raise Exception("No JSON object found in the model response")
    
    # Validate scores and evidence
    if "scores" not in assessment_result or "evidence" not in assessment_result:
        raise Exception("Response is missing required scores or evidence fields")
    
    # Ensure scores and evidence match the number of questions
    scores = assessment_result.get("scores", [])
    evidence = assessment_result.get("evidence", [])
    
    # Log the extracted scores
    app.logger.info(f"Extracted scores: {scores}")
    
    # Validate scores
    validated_scores = []
    for i in range(len(tool["questions"])):
        if i < len(scores) and isinstance(scores[i], (int, float)):
            # Cap scores to valid range (0-4)
            score = max(0, min(4, int(scores[i])))
            validated_scores.append(score)
        else:
            validated_scores.append(0)
    
    # Calculate total score and ensure it doesn't exceed max_score
    total_score = sum(validated_scores)
    if total_score > tool["max_score"]:
        # If total exceeds max, scale down proportionally
        scale_factor = tool["max_score"] / total_score
        validated_scores = [int(round(score * scale_factor)) for score in validated_scores]
        # Double-check the total again (due to rounding)
        if sum(validated_scores) > tool["max_score"]:
            # If still over, reduce the highest scores until within limit
            while sum(validated_scores) > tool["max_score"]:
                max_idx = validated_scores.index(max(validated_scores))
                validated_scores[max_idx] -= 1
    
    app.logger.info(f"Validated scores: {validated_scores}")
    
    # Validate evidence - strip any remaining annotations
    validated_evidence = []
    for i in range(len(tool["questions"])):
        if i < len(evidence) and evidence[i] and isinstance(evidence[i], str):
            # Remove any parenthetical annotations that might still be in the evidence
            cleaned_evidence = re.sub(r'\s*\(score \d\)\s*', '', evidence[i])
            validated_evidence.append(cleaned_evidence)
        else:
            validated_evidence.append("No specific evidence found in the session.")
    
    # Log the final result (without full evidence for brevity)
    app.logger.info(f"Final assessment result: {{'scores': {validated_scores}, 'evidence': (showing count only: {len(validated_evidence)})}}")
    
    return {
        "scores": validated_scores,
        "evidence": validated_evidence
    }