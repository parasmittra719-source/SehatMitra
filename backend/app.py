from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import time

app = Flask(__name__)
CORS(app)

# Use an environment variable to toggle between true ML and mock mode
# for faster development and testing if resources are limited.
USE_MOCK = os.environ.get("USE_MOCK", "true").lower() == "true"

print(f"Initializing SehatMitra Backend... (Mock mode: {USE_MOCK})")

if not USE_MOCK:
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
        import torch
        
        # We use a smaller model for the prototype if 8b is too heavy, or rely on 8B if available
        model_id = "google/gemma-4-8b-it" 
        print(f"Loading {model_id}...")
        
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(
            model_id, 
            device_map="auto", 
            torch_dtype=torch.float16
        )
        chat_pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer)
        print("Model loaded successfully!")
    except Exception as e:
        print(f"Failed to load model: {e}")
        print("Falling back to mock mode.")
        USE_MOCK = True

# Mock knowledge base for RAG (Retrieval-Augmented Generation)
KNOWLEDGE_BASE = {
    "fever": "Usually fever comes with body ache and fatigue. You should drink plenty of water, take rest, and take paracetamol if needed. If high fever persists for more than 3 days, consult a doctor immediately. [Source: WHO]",
    "bukhar": "आमतौर पर बुखार के साथ शरीर में दर्द और थकान होती है। आपको खूब पानी पीना चाहिए, आराम करना चाहिए। यदि 3 दिनों से अधिक समय तक तेज बुखार रहता है, तो तुरंत डॉक्टर से परामर्श लें। [Source: WHO]",
    "headache": "Headaches can be caused by stress, dehydration, or lack of sleep. Rest in a quiet, dark room and drink water. If it is severe or accompanied by other symptoms like vision changes, see a doctor. [Source: NHS]",
    "sar dard": "सिरदर्द तनाव, निर्जलीकरण, या नींद की कमी के कारण हो सकता है। शांत, अंधेरे कमरे में आराम करें और पानी पिएं। यदि यह गंभीर है, तो डॉक्टर से मिलें। [Source: Local Health Guidelines]"
}

def retrieve_context(query):
    """Simulate a vector DB retrieval for relevant health guidelines."""
    query_lower = query.lower()
    for key, info in KNOWLEDGE_BASE.items():
        if key in query_lower:
            return info
    return None

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    if not data or "query" not in data:
        return jsonify({"error": "No query provided"}), 400
        
    user_input = data.get("query", "")
    language = data.get("language", "hi") # default to Hindi
    
    # 1. Retrieval Step
    context = retrieve_context(user_input)
    
    # 2. Prompt Construction
    system_instruction = "You are SehatMitra, an offline AI health assistant for rural India. Answer health queries clearly and simply in the requested language. Do not diagnose, but provide general vetted health advice."
    
    if context:
        prompt = f"System: {system_instruction}\nContext (Official Guidelines): {context}\nPatient ({language}): {user_input}\nDoctor:"
    else:
        prompt = f"System: {system_instruction}\nPatient ({language}): {user_input}\nDoctor:"

    # 3. Model Generation
    try:
        if USE_MOCK:
            # Simulate latency
            time.sleep(1.5)
            if context:
                answer = f"Based on health guidelines: {context}\n\nPlease note: This is general advice. If symptoms persist, visit the nearest clinic."
            else:
                answer = "I understand you're feeling unwell. Please ensure you are resting and staying hydrated. Could you provide more specific symptoms so I can check the health guidelines? Remember to consult a local doctor for serious issues."
        else:
            # Run Gemma
            response = chat_pipeline(prompt, max_new_tokens=256, temperature=0.3, do_sample=True)
            answer = response[0]['generated_text'].split("Doctor:")[-1].strip()
            
        return jsonify({"answer": answer, "retrieved_context": context is not None})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "running", "mode": "mock" if USE_MOCK else "gemma-4"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
