import os
import json
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from groq import Groq
from dotenv import load_dotenv
from app.model.problem import Problem
from app.repository import CityRepository
from geopy.geocoders import Nominatim

# Ρύθμιση φακέλου μεταφορτώσεων (uploads) για την αποθήκευση φωτογραφιών στο filesystem
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Φόρτωση μεταβλητών περιβάλλοντος (π.χ. API keys) από το αρχείο .env
load_dotenv()

# Αρχικοποίηση της εφαρμογής Flask (Πλατφόρμα / Backend)
app = Flask(__name__)

# Μέγιστο μέγεθος αιτήματος (φωτογραφίας): 10 MB, πάνω από αυτό το Flask απαντά 413
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

# Σύνδεση με το Αποθετήριο (Repository) της Βάσης Δεδομένων
repo = CityRepository()


# Αρχικοποίηση Geocoding (Υποσύστημα Εξωτερικών APIs: OpenStreetMap Nominatim)
geolocator = Nominatim(user_agent="city_report_app")


def call_groq_ai(title, description):
    """
    Υποσύστημα Τεχνητής Νοημοσύνης (Ολοκλήρωση με Groq API / Llama3).
    Αναλύει τον τίτλο και την περιγραφή που έδωσε ο πολίτης και μέσω Prompt Engineering
    επιστρέφει αυτόματα:
    α) Την κατηγορία του προβλήματος (1-5).
    β) Την προτεραιότητα (Low, Medium, High).
    """
    # Ανάκτηση του API key από τις μεταβλητές περιβάλλοντος
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("[AI Error] GROQ_API_KEY is missing from environment variables!")
        return 5, "Medium"  # Ασφαλής εναλλακτική (fallback) αν λείπει το κλειδί

    try:
        # Αρχικοποίηση του πελάτη Groq
        client = Groq(api_key=api_key)
        
        # Οδηγίες συστήματος (System Prompt) για την αυστηρή επιστροφή σχήματος JSON
        system_prompt = """
        You are an AI assistant for a Smart City Issue Tracker. Your job is to analyze the user's report description and return a JSON object with exactly two keys:
        1. "category_id": An integer from 1 to 5 based on these rules:
           - 1 if it relates to Roadworks/Potholes/Pavement issues (Οδοποιία)
           - 2 if it relates to Broken street lights/Dark areas (Ηλεκτροφωτισμός)
           - 3 if it relates to Garbage/Overflowing bins/Cleanliness (Καθαριότητα)
           - 4 if it relates to Broken trees/Parks/Uncut grass (Πράσινο)
           - 5 for anything else (Άλλο)
        2. "priority": A string that must be exactly one of these: "Low", "Medium", "High", depending on how urgent or dangerous the issue is to public safety.

        You must respond ONLY with the raw JSON object. Do not include any markdown styling, backticks, introduction, or explanation.
        Example output: {"category_id": 3, "priority": "High"}
        """

        # Σύγχρονη κλήση (synchronous call) στο Groq API με το μοντέλο llama-3.3-70b-versatile
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze this issue. Title: {title}. Description: {description}"}
            ],
            temperature=0.0, # Low temperature for consistent and deterministic results
            response_format={"type": "json_object"} # Force Groq to return valid JSON
        )

        # Ανάλυση του JSON κειμένου που επέστρεψε το LLM
        ai_response = json.loads(completion.choices[0].message.content)
        category_id = int(ai_response.get("category_id", 1))
        priority = ai_response.get("priority", "Medium")
        
        print(f"[AI Success] Classified as Category: {category_id}, Priority: {priority}")
        return category_id, priority

    except Exception as e:
        print(f"[AI Exception] Failed to call Groq API: {e}")
        return 5, "Medium"  # Ασφαλής εναλλακτική (fallback) αν λείπει το κλειδί

@app.route('/api/problems', methods=['POST'])
def create_problem():
    """
    1. ΥΠΟΒΟΛΗ ΝΕΑΣ ΑΝΑΦΟΡΑΣ (POST)
    Ο πολίτης αποστέλλει (ανώνυμα): τίτλο, περιγραφή και συντεταγμένες (latitude, longitude).
    Το σύστημα αυτόματα εντοπίζει τη διεύθυνση (μέσω Geopy) και την κατηγορία/προτεραιότητα (μέσω Groq AI).
    Επιστρέφει το μοναδικό Ticket ID.
    """
    # 1. Ανάγνωση των εισερχόμενων JSON δεδομένων
    data = request.get_json(silent=True) or {}
    
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        # 2. Ανάκτηση πεδίων από το σώμα (body) του αιτήματος
        title = data.get('title')
        description = data.get('description')
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        # Έλεγχος επικύρωσης υποχρεωτικών πεδίων πριν την επεξεργασία
        if not title or not description or latitude is None or longitude is None:
            return jsonify({"error": "Τα πεδία title, description, latitude και longitude είναι υποχρεωτικά"}), 400
        

        # Έλεγχος για διπλότυπο: Αναφορά με τον ίδιο τίτλο και τις ίδιες (ή πολύ κοντινές) συντεταγμένες
        existing = repo.find_duplicate(title, latitude, longitude)
        if existing:
            repo.upvote_problem(existing['id'])
            return jsonify({
                "message": "Υπάρχει ήδη αναφορά για αυτό το πρόβλημα. Προστέθηκε upvote!",
                "ticket_id": existing['ticket_id'],
                "upvotes": existing['upvotes'] + 1
            }), 200

        # Α) [Εξωτερικό API] Reverse Geocoding: Μετατροπή Συντεταγμένων (Lat/Lon) σε αναγνώσιμη διεύθυνση
        address = "Unknown Address"
        try:
            location = geolocator.reverse((latitude, longitude), timeout=10)
            if location:
                address = location.address
        except Exception as geo_err:
            print(f"Geocoding error: {geo_err}")

        # Β) [Υποσύστημα AI] Αυτόματη κατηγοριοποίηση και αξιολόγηση προτεραιότητας μέσω Groq
        category_id, priority = call_groq_ai(title, description)


        # Γ) Δημιουργία του αντικειμένου Problem με τα εμπλουτισμένα δεδομένα
        new_problem = Problem(
            title=title,
            description=description,
            latitude=latitude,
            longitude=longitude,
            address=address,         # Automatically filled by Geopy
            category_id=category_id, # Automatically filled by AI
            priority=priority,       # Automatically filled by AI
            photo_path=data.get('photo_path')
        )

        # Δ) Αποθήκευση της αναφοράς στη βάση δεδομένων
        # Αν η εγγραφή αποτύχει, δεν δίνουμε ticket στον πολίτη
        if not repo.add_problem(new_problem):
            return jsonify({"error": "Η αναφορά δεν αποθηκεύτηκε. Δοκίμασε ξανά."}), 500

        return jsonify({
            "message": "Report successfully created!",
            "ticket_id": new_problem.ticket_id,
            "auto_assigned_address": address,
            "auto_category_id": category_id,
            "auto_priority": priority
        }), 201

    except Exception as e:
        # Το σφάλμα γράφεται μόνο στα logs, ο πολίτης παίρνει γενικό μήνυμα
        print(f"[Σφάλμα] {e}")
        return jsonify({"error": "Κάτι πήγε στραβά. Δοκίμασε ξανά."}), 500


@app.route('/api/problems', methods=['GET'])
def get_filtered_problems():
    """
    2. ΑΝΑΖΗΤΗΣΗ & ΦΙΛΤΡΑΡΙΣΜΑ ΠΡΟΒΛΗΜΑΤΩΝ (GET)
    Υποστηρίζει φιλτράρισμα μέσω παραμέτρων URL (π.χ. ?category_id=1&status_id=1) 
    και ταξινόμηση (π.χ. ?sort=created_at). Επιστρέφει λίστα JSON.
    """
    try:
        # Ανάκτηση όλων των εγγραφών από τη βάση δεδομένων
        problems = repo.get_problems()  
        
        # Ανάκτηση φίλτρων από τις παραμέτρους (query parameters) του URL
        category = request.args.get('category_id')
        status = request.args.get('status_id')
        date_from = request.args.get('date_from')  # format: YYYY-MM-DD
        date_to = request.args.get('date_to')      # format: YYYY-MM-DD
        sort_by = request.args.get('sort', 'created_at')

        # Εφαρμογή λογικής φιλτραρίσματος βάσει των παρεχόμενων παραμέτρων (List Comprehensions)
        if category:
            problems = [p for p in problems if p['category_id'] == int(category)]
        if status:
            problems = [p for p in problems if p['status_id'] == int(status)]
        if date_from:
            problems = [p for p in problems if p.get('created_at', '') >= date_from]
        if date_to:
            problems = [p for p in problems if p.get('created_at', '') <= date_to + 'T23:59:59']
            
        # Εφαρμογή λογικής ταξινόμησης (προεπιλογή: από το νεότερο στο παλαιότερο)
        problems.sort(key=lambda x: x.get(sort_by, ''), reverse=True)

        return jsonify(problems), 200
    except Exception as e:
        print(f"[Σφάλμα] {e}")
        return jsonify({"error": "Κάτι πήγε στραβά. Δοκίμασε ξανά."}), 500


@app.route('/api/problems/<string:ticket_id>', methods=['PUT'])
def update_problem_description(ticket_id):
    """
    3. ΕΝΗΜΕΡΩΣΗ ΥΠΑΡΧΟΝΤΟΣ ΠΡΟΒΛΗΜΑΤΟΣ (PUT μέσω Ticket ID)
    Επιτρέπει στον πολίτη να τροποποιήσει/προσθέσει πληροφορίες στην περιγραφή του 
    προβλήματος, χρησιμοποιώντας το μοναδικό του Ticket ID.
    """
    data = request.get_json(silent=True) or {}
    new_description = data.get('description')
    
    if not new_description:
        return jsonify({"error": "New description is required"}), 400

    # Εκτέλεση ενημέρωσης μέσω CityRepository (Repository Pattern)
    updated = repo.update_description(ticket_id, new_description)
    if not updated:
        return jsonify({"error": "Ticket ID not found"}), 404
    return jsonify({"message": f"Ticket {ticket_id} updated successfully!"}), 200


@app.route('/api/problems/<string:ticket_id>', methods=['GET'])
def get_problem_by_ticket(ticket_id):
    """
    ΑΝΑΚΤΗΣΗ ΠΡΟΒΛΗΜΑΤΟΣ ΜΕΣΩ TICKET ID (GET)
    Επιτρέπει στον πολίτη να παρακολουθήσει την κατάσταση της συγκεκριμένης αναφοράς του.
    """
    try:
        # Ανάκτηση αναφοράς μέσω CityRepository (Repository Pattern)
        problem = repo.get_problem_by_ticket(ticket_id)
        if not problem:
            return jsonify({"error": "Ticket ID not found"}), 404
        return jsonify(problem), 200
    except Exception as e:
        print(f"[Σφάλμα] {e}")
        return jsonify({"error": "Κάτι πήγε στραβά. Δοκίμασε ξανά."}), 500


@app.route('/api/problems/<string:ticket_id>/upvote', methods=['POST'])
def upvote_problem(ticket_id):
    """
    4. UPVOTE (ΘΕΤΙΚΗ ΨΗΦΟΣ) ΠΡΟΒΛΗΜΑΤΟΣ (POST)
    Αυξάνει τον μετρητή των θετικών ψήφων (upvotes) κατά 1.
    """
    try:
        # Εύρεση αναφοράς μέσω CityRepository και έλεγχος ύπαρξης
        problem = repo.get_problem_by_ticket(ticket_id)
        if not problem:
            return jsonify({"error": "Ticket ID not found"}), 404
        # Αύξηση upvotes μέσω CityRepository (Repository Pattern)
        repo.upvote_problem(problem['id'])
        return jsonify({"message": f"Problem {ticket_id} upvoted successfully!"}), 200
    except Exception as e:
        print(f"[Σφάλμα] {e}")
        return jsonify({"error": "Κάτι πήγε στραβά. Δοκίμασε ξανά."}), 500


@app.route('/api/problems/<string:ticket_id>/photo', methods=['POST'])
def upload_photo(ticket_id):
    """
    5. ΜΕΤΑΦΟΡΤΩΣΗ ΦΩΤΟΓΡΑΦΙΑΣ (POST μέσω Ticket ID)
    Δέχεται ένα αίτημα multipart/form-data με ένα πεδίο αρχείου (file field) με όνομα 'photo'.
    Αποθηκεύει το αρχείο στον φάκελο /uploads/ και ενημερώνει το photo_path στη βάση δεδομένων.
    """
    if 'photo' not in request.files:
        return jsonify({"error": "Δεν παρέχθηκε αρχείο φωτογραφίας (πεδίο: photo)"}), 400

    file = request.files['photo']
    if file.filename == '':
        return jsonify({"error": "Κενό όνομα αρχείου"}), 400

    allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
    # Εξαγωγή και έλεγχος της κατάληξης (extension) του αρχείου
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in allowed_extensions:
        return jsonify({"error": f"Μη αποδεκτή μορφή αρχείου. Επιτρεπόμενα: {', '.join(allowed_extensions)}"}), 400

    # Κανονικοποίηση (normalization) του Ticket ID και δημιουργία ασφαλούς ονόματος αρχείου
    normalized_id = ticket_id.upper().strip()
    filename = f"{normalized_id}_{secure_filename(file.filename)}"
    save_path = os.path.join(UPLOAD_FOLDER, filename)

    # Αποθήκευση στο filesystem
    file.save(save_path)

    # Ενημέρωση της διαδρομής (path) στη βάση δεδομένων
    relative_path = f"uploads/{filename}"
    updated = repo.update_photo_path(normalized_id, relative_path)
    if not updated:
        return jsonify({"error": "Ticket ID δεν βρέθηκε"}), 404

    return jsonify({"message": "Φωτογραφία αποθηκεύτηκε επιτυχώς", "photo_path": relative_path}), 200