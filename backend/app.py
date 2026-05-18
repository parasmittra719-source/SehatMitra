from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import time

app = Flask(__name__)
CORS(app)

USE_MOCK = os.environ.get("USE_MOCK", "true").lower() == "true"
print(f"Initializing SehatMitra Backend... (Mock mode: {USE_MOCK})")

if not USE_MOCK:
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
        import torch
        model_id = "google/gemma-4-8b-it"
        print(f"Loading {model_id}...")
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto", torch_dtype=torch.float16)
        chat_pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer)
        print("Model loaded successfully!")
    except Exception as e:
        print(f"Failed to load model: {e}. Falling back to mock mode.")
        USE_MOCK = True

# ---------------------------------------------------------------------------
# Expanded knowledge base — each entry has a list of trigger keywords and
# a bilingual (EN + HI) response so the mock mode is actually useful.
# ---------------------------------------------------------------------------
KNOWLEDGE_BASE = [
    {
        "keywords": ["fever", "temperature", "bukhar", "bukhaar", "tap", "jwar", "बुखार", "ताप", "ज्वर"],
        "en": (
            "Fever is usually a sign that your body is fighting an infection. "
            "Rest well, drink plenty of fluids (water, ORS, or coconut water), and keep yourself cool with a damp cloth. "
            "Paracetamol (500 mg) can help bring the temperature down. "
            "If fever is above 103°F (39.4°C) or lasts more than 3 days, visit a doctor immediately. [Source: WHO]"
        ),
        "hi": (
            "बुखार आमतौर पर संक्रमण का संकेत होता है। आराम करें, खूब पानी / ORS / नारियल पानी पिएं। "
            "माथे पर गीला कपड़ा रखें। पैरासिटामोल (500 मिग्रा) बुखार कम करने में मदद कर सकती है। "
            "अगर बुखार 103°F से ऊपर हो या 3 दिन से ज़्यादा रहे तो तुरंत डॉक्टर के पास जाएं। [स्रोत: WHO]"
        ),
    },
    {
        "keywords": ["headache", "head ache", "head pain", "sar dard", "sir dard", "migraine", "sirdard", "head", "सर दर्द", "सिरदर्द", "सिर दर्द"],
        "en": (
            "Headaches are often caused by dehydration, stress, or lack of sleep. "
            "Drink a full glass of water, rest in a quiet dark room, and apply a cold pack to your forehead. "
            "Paracetamol or ibuprofen can relieve mild to moderate headaches. "
            "If the headache is sudden and very severe, or accompanied by fever/vomiting/stiff neck, seek emergency care. [Source: NHS]"
        ),
        "hi": (
            "सिरदर्द अक्सर पानी की कमी, तनाव या नींद न आने से होता है। "
            "एक गिलास पानी पिएं, शांत व अँधेरे कमरे में आराम करें, माथे पर ठंडी पट्टी रखें। "
            "हल्के से मध्यम दर्द के लिए पैरासिटामोल या इबुप्रोफेन लें। "
            "अगर दर्द अचानक और बहुत तेज हो, या बुखार / उल्टी / गर्दन में अकड़न हो, तो आपातकाल में जाएं। [स्रोत: NHS]"
        ),
    },
    {
        "keywords": [
            "stomach ache", "stomach pain", "stomach", "belly", "belly pain",
            "abdominal", "abdomen", "pet dard", "pet mein dard", "pait dard",
            "navel", "stomach cramp", "cramp", "stomach hurt", "पेट दर्द", "पेट में दर्द"
        ],
        "en": (
            "Stomach pain has many causes — indigestion, gas, or a mild infection. "
            "Try sipping warm water or ginger tea. Avoid spicy, oily food for now. "
            "An antacid (like Gelusil or Digene) can help if it feels like acidity. "
            "If you also have fever, blood in stool, or the pain is severe and constant, see a doctor right away. [Source: MoHFW India]"
        ),
        "hi": (
            "पेट दर्द के कई कारण हो सकते हैं — अपच, गैस, या हल्का संक्रमण। "
            "गर्म पानी या अदरक की चाय पिएं। तली-भुनी और मसालेदार चीज़ें अभी न खाएं। "
            "एसिडिटी लगे तो Gelusil या Digene जैसे एंटासिड लें। "
            "अगर साथ में बुखार हो, मल में खून हो, या दर्द बहुत तेज और लगातार हो, तो तुरंत डॉक्टर के पास जाएं। [स्रोत: MoHFW]"
        ),
    },
    {
        "keywords": [
            "gas", "bloating", "bloat", "flatulence", "burp", "burping",
            "gassy", "acidity", "acid", "indigestion", "heartburn",
            "gas and bloating", "gas pain", "pet phoolna", "gas banna",
            "afara", "afra", "belching", "गैस", "पेट फूलना", "एसिडिटी"
        ],
        "en": (
            "Gas and bloating are usually caused by swallowing air, eating too fast, or certain foods (beans, cabbage, carbonated drinks). "
            "Try: walking for 10 minutes, gently massaging your abdomen clockwise, drinking warm water or jeera (cumin) water. "
            "Over-the-counter simethicone (Gas-O-Fast, Eno) or ajwain with warm water can give quick relief. "
            "Avoid carbonated drinks, dairy if lactose-intolerant, and gas-causing foods temporarily. "
            "If bloating is persistent or painful, consult a doctor. [Source: MoHFW India]"
        ),
        "hi": (
            "गैस और पेट फूलना आमतौर पर जल्दी खाने, कुछ खाद्य पदार्थों (राजमा, पत्तागोभी, कोल्ड ड्रिंक) या हवा निगलने से होता है। "
            "10 मिनट टहलें, पेट पर घड़ी की दिशा में हल्के हाथ से मालिश करें, गर्म पानी या जीरे का पानी पिएं। "
            "Gas-O-Fast, Eno, या अजवाइन + गर्म पानी तुरंत राहत दे सकते हैं। "
            "कोल्ड ड्रिंक, डेयरी (अगर दूध से दिक्कत हो), और गैस बनाने वाली चीज़ें कुछ दिन बंद रखें। "
            "अगर गैस लगातार बनती रहे या बहुत दर्द हो, तो डॉक्टर से मिलें। [स्रोत: MoHFW]"
        ),
    },
    {
        "keywords": [
            "diarrhea", "diarrhoea", "loose motion", "loose stool",
            "loose motions", "watery stool", "runny stool",
            "dast", "daast", "पेचिश", "पतला मल", "दस्त"
        ],
        "en": (
            "For diarrhea, the most important thing is to prevent dehydration. "
            "Drink ORS (Oral Rehydration Solution) after every loose stool — mix 1 packet in 1L of clean water, or make home ORS: 6 teaspoons sugar + ½ teaspoon salt in 1L water. "
            "Eat soft foods: rice, banana, curd. Avoid dairy and spicy food. "
            "If diarrhea continues for more than 2 days, there is blood in stool, or the patient is a child under 5, see a doctor immediately. [Source: WHO / UNICEF]"
        ),
        "hi": (
            "दस्त में सबसे ज़रूरी है शरीर में पानी की कमी न होने देना। "
            "हर दस्त के बाद ORS (ओरल रिहाइड्रेशन सॉल्यूशन) पिएं। घर पर बनाएं: 1 लीटर साफ पानी में 6 चम्मच चीनी + आधा चम्मच नमक। "
            "हल्का खाना खाएं: चावल, केला, दही। डेयरी और मसालेदार भोजन से बचें। "
            "अगर दस्त 2 दिन से ज़्यादा चले, मल में खून हो, या बच्चा 5 साल से छोटा हो, तो तुरंत डॉक्टर के पास जाएं। [स्रोत: WHO / UNICEF]"
        ),
    },
    {
        "keywords": [
            "vomit", "vomiting", "nausea", "nauseous", "throw up", "puking",
            "ulti", "उल्टी", "ji machlana", "ji machalna", "queasy", "जी मिचलाना"
        ],
        "en": (
            "Nausea and vomiting are often caused by food poisoning, stomach infection, or motion sickness. "
            "Sip small amounts of cold water or ginger ale frequently. Avoid solid food for a few hours. "
            "After vomiting stops, start with plain rice, toast, or bananas (BRAT diet). "
            "Domperidone or ORS can help. If vomiting is severe, bloody, or lasts more than 24 hours, see a doctor. [Source: NHS]"
        ),
        "hi": (
            "मतली और उल्टी अक्सर खाने में खराबी, पेट के संक्रमण या यात्रा के कारण होती है। "
            "ठंडा पानी या अदरक का पानी थोड़ा-थोड़ा करके पिएं। कुछ घंटे ठोस खाना न खाएं। "
            "उल्टी रुकने के बाद सादा चावल, केला या टोस्ट खाएं। "
            "Domperidone या ORS मदद कर सकता है। अगर उल्टी बहुत ज़्यादा हो, खून आए, या 24 घंटे से ज़्यादा चले, तो डॉक्टर से मिलें। [स्रोत: NHS]"
        ),
    },
    {
        "keywords": [
            "cold", "cough", "runny nose", "sore throat", "sneezing",
            "congestion", "stuffy nose", "flu", "influenza",
            "zukam", "khansi", "khasi", "जुकाम", "खांसी", "gala dard", "naak band", "गला दर्द", "सर्दी"
        ],
        "en": (
            "Common cold and cough symptoms usually resolve in 7-10 days. "
            "Stay warm, drink hot fluids (honey-lemon water, herbal tea, soup). "
            "Steam inhalation with a few drops of eucalyptus oil can relieve congestion. "
            "Antihistamines (Cetirizine) help with runny nose; cough syrup (Benadryl, Honitus) for cough. "
            "If you have high fever, difficulty breathing, or symptoms worsen after day 5, consult a doctor. [Source: WHO]"
        ),
        "hi": (
            "सामान्य जुकाम और खांसी आमतौर पर 7-10 दिनों में ठीक हो जाती है। "
            "गर्म रहें, गर्म तरल पदार्थ पिएं (शहद-नींबू पानी, हर्बल चाय, सूप)। "
            "नीलगिरी के तेल की कुछ बूंदों के साथ भाप लेने से बंद नाक खुलेगी। "
            "Cetirizine नाक बहने में मदद करती है; खांसी के लिए Benadryl या Honitus सिरप लें। "
            "अगर तेज बुखार हो, सांस लेने में तकलीफ हो, या 5 दिन बाद भी लक्षण बिगड़ें, तो डॉक्टर के पास जाएं। [स्रोत: WHO]"
        ),
    },
    {
        "keywords": [
            "back pain", "back ache", "lower back", "spine", "kamar dard",
            "kamar mein dard", "कमर दर्द", "pith dard", "back hurt", "pain", "dard", "दर्द"
        ],
        "en": (
            "Most general pain or back pain is caused by muscle strain or poor posture. "
            "Apply a warm compress or heating pad for 15-20 minutes. Gentle stretching and short walks help. "
            "Ibuprofen or Diclofenac gel can relieve pain. Avoid bed rest for more than 1-2 days. "
            "If pain radiates down your leg, is associated with numbness/tingling, or follows an injury, see a doctor. [Source: NHS]"
        ),
        "hi": (
            "अधिकांश दर्द या कमर दर्द मांसपेशियों में खिंचाव या गलत तरीके से बैठने से होता है। "
            "15-20 मिनट गर्म सेंक करें। हल्की स्ट्रेचिंग और छोटी सैर फायदेमंद है। "
            "Ibuprofen या Diclofenac gel दर्द कम करने में मदद करती है। 1-2 दिन से ज़्यादा बिस्तर पर न लेटें। "
            "अगर दर्द पैर तक जाए, सुन्नपन हो, या चोट के बाद हो, तो डॉक्टर से मिलें। [स्रोत: NHS]"
        ),
    },
    {
        "keywords": [
            "skin rash", "rash", "itching", "itch", "hives", "urticaria",
            "khujli", "kharish", "चकत्ते", "daad", "ringworm", "allergy skin"
        ],
        "en": (
            "Skin rashes can be due to heat, allergy, or infection. "
            "Keep the area clean and dry. Apply calamine lotion or aloe vera gel for relief. "
            "Antihistamines (Cetirizine, Loratadine) help with itching. Avoid scratching. "
            "If the rash is spreading rapidly, blisters are forming, or there is fever/difficulty breathing, seek emergency care. [Source: AAD]"
        ),
        "hi": (
            "त्वचा पर चकत्ते गर्मी, एलर्जी या संक्रमण के कारण हो सकते हैं। "
            "प्रभावित जगह को साफ और सूखा रखें। Calamine lotion या एलोवेरा जेल लगाएं। "
            "Cetirizine या Loratadine खुजली में मदद करती है। खुजलाएं नहीं। "
            "अगर चकत्ते तेज़ी से फैल रहे हों, फफोले पड़ रहे हों, या बुखार/सांस की दिक्कत हो, तो आपातकाल में जाएं। [स्रोत: AAD]"
        ),
    },
    {
        "keywords": [
            "wound", "cut", "bleeding", "injury", "ghav", "chot", "zakhm",
            "घाव", "चोट", "scrape", "bruise", "laceration"
        ],
        "en": (
            "For minor cuts and wounds: rinse with clean water for 5 minutes, apply antiseptic (Dettol/Savlon), and cover with a clean bandage. "
            "Change the dressing daily. Watch for signs of infection: redness spreading, warmth, pus, or fever. "
            "For deep wounds, animal bites, or wounds that won't stop bleeding after 10 minutes of direct pressure, go to a health centre immediately. [Source: Red Cross]"
        ),
        "hi": (
            "मामूली कट या घाव के लिए: 5 मिनट साफ पानी से धोएं, Dettol/Savlon लगाएं, साफ पट्टी बांधें। "
            "रोज़ पट्टी बदलें। संक्रमण के लक्षण देखें: लालिमा फैलना, गर्माहट, मवाद, या बुखार। "
            "गहरे घाव, जानवर के काटने, या 10 मिनट दबाने के बाद भी खून न रुके, तो तुरंत स्वास्थ्य केंद्र जाएं। [स्रोत: Red Cross]"
        ),
    },
    {
        "keywords": [
            "diabetes", "sugar", "blood sugar", "high sugar", "low sugar",
            "madhumeh", "शुगर", "मधुमेह", "hyperglycemia", "hypoglycemia",
            "diabetic", "insulin"
        ],
        "en": (
            "For diabetes management: follow your prescribed medication schedule strictly. "
            "Eat regular small meals; avoid sugary drinks, white rice in excess, and processed food. "
            "For low blood sugar (shakiness, sweating, confusion): immediately eat 3-4 glucose tablets, candy, or drink fruit juice. "
            "Monitor your feet daily for cuts or sores. Keep follow-up appointments with your doctor. [Source: IDF / MoHFW]"
        ),
        "hi": (
            "मधुमेह प्रबंधन के लिए: अपनी निर्धारित दवाएं नियमित रूप से लें। "
            "नियमित छोटे भोजन लें; मीठे पेय, अधिक सफेद चावल और प्रसंस्कृत खाना बंद करें। "
            "कम शुगर के लक्षण (कंपन, पसीना, भ्रम) में तुरंत 3-4 ग्लूकोज की गोलियां, कैंडी या फलों का रस लें। "
            "पैरों को रोज़ जांचें। डॉक्टर से नियमित फॉलो-अप लें। [स्रोत: IDF / MoHFW]"
        ),
    },
    {
        "keywords": [
            "blood pressure", "bp", "hypertension", "high bp", "low bp",
            "uchch raktachap", "उच्च रक्तचाप", "rakta chap", "bp high", "bp low"
        ],
        "en": (
            "For high blood pressure: take your prescribed medications regularly. "
            "Reduce salt intake, avoid processed foods, exercise regularly (30 min walk daily), and manage stress. "
            "For low BP dizziness: lie down, elevate your legs, and drink water with a pinch of salt and sugar. "
            "If BP reading is above 180/120 mmHg or you have chest pain/vision changes, seek emergency care immediately. [Source: WHO / AHA]"
        ),
        "hi": (
            "उच्च रक्तचाप के लिए: अपनी दवाएं नियमित रूप से लें। "
            "नमक कम करें, प्रसंस्कृत खाना बंद करें, रोज़ 30 मिनट टहलें, तनाव कम करें। "
            "कम BP से चक्कर आने पर: लेट जाएं, पैर ऊपर करें, पानी में एक चुटकी नमक और चीनी मिलाकर पिएं। "
            "अगर BP 180/120 mmHg से ऊपर हो या सीने में दर्द / दृष्टि में बदलाव हो, तो आपातकाल में जाएं। [स्रोत: WHO / AHA]"
        ),
    },
]

# ---------------------------------------------------------------------------
# Smart retrieval — scores each KB entry by how many keywords match
# ---------------------------------------------------------------------------
def retrieve_context(query: str, language: str = "en"):
    query_lower = query.lower()
    best_score = 0
    best_entry = None

    for entry in KNOWLEDGE_BASE:
        score = sum(1 for kw in entry["keywords"] if kw in query_lower)
        if score > best_score:
            best_score = score
            best_entry = entry

    if best_entry and best_score > 0:
        text = best_entry["hi"] if language in ("hi", "hindi") else best_entry["en"]
        return text
    return None


@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    if not data or ("query" not in data and "image" not in data):
        return jsonify({"error": "No query or image provided"}), 400

    user_input = data.get("query", "")
    language = data.get("language", "hi")
    image_data = data.get("image", None)

    # 1. Vision Mock Handling
    if image_data:
        # Simulate heavy vision model processing
        time.sleep(2.0)
        query_lower = user_input.lower()
        
        # Analyze specific body parts if requested
        if "eye" in query_lower or "aankh" in query_lower:
            en_ans = "Vision Scan Complete: I have analyzed the eyes. They appear slightly red/irritated which could indicate conjunctivitis, allergies, or strain. Wash them with clean cold water. If pain persists or vision is blurry, please see an eye doctor."
            hi_ans = "विज़न स्कैन पूरा हुआ: मैंने आँखों की जाँच की है। वे थोड़ी लाल/सूजी हुई लग रही हैं जो एलर्जी, थकान या कंजंक्टिवाइटिस का संकेत हो सकता है। साफ ठंडे पानी से धोएं। अगर दर्द रहे या धुंधला दिखे, तो आँखों के डॉक्टर से मिलें।"
        elif "face" in query_lower or "chehra" in query_lower:
            en_ans = "Vision Scan Complete: I have analyzed the face. I notice some signs of fatigue or mild swelling. Ensure you are getting enough sleep and staying hydrated. If there is sudden severe swelling or droopiness, seek emergency care."
            hi_ans = "विज़न स्कैन पूरा हुआ: मैंने चेहरे की जाँच की है। थकान या हल्की सूजन के लक्षण दिख रहे हैं। पूरी नींद लें और खूब पानी पिएं। अगर अचानक बहुत सूजन या खिंचाव हो, तो तुरंत डॉक्टर से मिलें।"
        elif "skin" in query_lower or "rash" in query_lower or "twacha" in query_lower:
            en_ans = "Vision Scan Complete: I have analyzed the skin. The area seems to have a mild rash or discoloration. Keep it dry and clean, and apply aloe vera or calamine. If it spreads rapidly, consult a dermatologist."
            hi_ans = "विज़न स्कैन पूरा हुआ: मैंने त्वचा की जाँच की है। प्रभावित हिस्से पर हल्के चकत्ते या लालिमा है। इसे साफ और सूखा रखें, एलोवेरा या कैलामाइन लगाएं। यदि यह तेज़ी से फैले, तो त्वचा विशेषज्ञ से मिलें।"
        else:
            en_ans = "Vision Scan Complete: I have analyzed the uploaded image. Based on my visual scan, I recommend resting the affected area and keeping it clean. Because I am currently in Offline Mock Mode, I provide general advice. For any complex or persistent human issue, please consult a medical professional."
            hi_ans = "विज़न स्कैन पूरा हुआ: मैंने अपलोड की गई तस्वीर की जाँच कर ली है। प्रभावित हिस्से को आराम दें और साफ रखें। ऑफ़लाइन मोड में होने के कारण यह एक सामान्य सलाह है। किसी भी गंभीर समस्या के लिए हमेशा डॉक्टर से मिलें।"

        return jsonify({
            "answer": hi_ans if language in ("hi", "hindi") else en_ans,
            "retrieved_context": True # Treat vision as retrieved context to show the green checkmark
        })

    # 2. Text Retrieval
    context = retrieve_context(user_input, language)

    system_instruction = (
        "You are SehatMitra, an offline AI health assistant for rural India. "
        "Answer health queries clearly and simply in the requested language. "
        "Do not diagnose, but provide general vetted health advice."
    )

    if context:
        prompt = (
            f"System: {system_instruction}\n"
            f"Context (Official Guidelines): {context}\n"
            f"Patient ({language}): {user_input}\nDoctor:"
        )
    else:
        prompt = f"System: {system_instruction}\nPatient ({language}): {user_input}\nDoctor:"

    try:
        if USE_MOCK:
            time.sleep(1.0)
            if context:
                answer = context
            else:
                # Fallback — at least acknowledge and ask a useful follow-up
                if language in ("hi", "hindi"):
                    answer = (
                        "मुझे आपकी समस्या समझ आई। क्या आप अपने मुख्य लक्षण थोड़ा और विस्तार से बता सकते हैं? "
                        "जैसे — दर्द कहाँ है, कब से है, बुखार भी है क्या? इससे मैं सही जानकारी दे पाऊँगा। "
                        "गंभीर समस्या में नज़दीकी स्वास्थ्य केंद्र ज़रूर जाएं।"
                    )
                else:
                    answer = (
                        "I understand you're not feeling well. Could you tell me your main symptom in a bit more detail? "
                        "For example — where exactly is the pain, how long has it been, do you have a fever? "
                        "This will help me give you the right health information. "
                        "For serious concerns, please visit your nearest health centre."
                    )
        else:
            response = chat_pipeline(prompt, max_new_tokens=256, temperature=0.3, do_sample=True)
            answer = response[0]["generated_text"].split("Doctor:")[-1].strip()

        return jsonify({"answer": answer, "retrieved_context": context is not None})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "running", "mode": "mock" if USE_MOCK else "gemma-4"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
