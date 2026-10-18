"""
Σελίδα Αναφορών (Reports) - Admin Dashboard (Streamlit)
Παρέχει στους διαχειριστές τη δυνατότητα να φιλτράρουν το σύνολο των προβλημάτων,
να προβάλλουν αναλυτικά τα στοιχεία κάθε αναφοράς (συμπεριλαμβανομένων φωτογραφιών 
και δεδομένων από εξωτερικά APIs) και να ενημερώνουν την κατάστασή τους.
"""
import streamlit as st
import pandas as pd
import time
import requests
import os
import sys
from dotenv import load_dotenv

# Προσθήκη του ριζικού φακέλου στο sys.path για την εισαγωγή των τοπικών modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.repository import CityRepository

# Φόρτωση API key από το .env
load_dotenv()
OWM_API_KEY = os.getenv("OWM_API_KEY")

# Ρίζα του project (ένας φάκελος πάνω από το pages/) — για να βρίσκουμε τις φωτογραφίες
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ── Βοηθητικές συναρτήσεις εξωτερικών APIs ────────────────────────

def get_weather(lat, lon):
    """Ανακτά καιρό από OpenWeatherMap."""
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": OWM_API_KEY,
            "units": "metric",
            "lang": "el"
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if response.status_code == 200:
            desc  = data["weather"][0]["description"].capitalize()
            temp  = data["main"]["temp"]
            feels = data["main"]["feels_like"]
            hum   = data["main"]["humidity"]
            wind  = data["wind"]["speed"]
            return f"🌤 {desc} | 🌡 {temp}°C (αίσθηση {feels}°C) | 💧 {hum}% | 💨 {wind} m/s"
        else:
            return "⚠️ Δεν ήταν δυνατή η ανάκτηση καιρού."
    except Exception as e:
        return f"⚠️ Σφάλμα καιρού: {e}"


def resolve_photo_path(photo_path):
    """
    Επιστρέφει μια έγκυρη διαδρομή/URL για την εικόνα της αναφοράς, ή None.
    Καλύπτει διάφορες περιπτώσεις για το πώς μπορεί να έχει αποθηκευτεί το path
    στη βάση (απόλυτο, σχετικό από τη ρίζα, μέσα στον φάκελο uploads/, ή URL).
    """
    if not photo_path or str(photo_path).strip().lower() in ("", "nan", "none"):
        return None

    p = str(photo_path).strip()

    # 1. Αν είναι URL, το επιστρέφουμε ως έχει
    if p.startswith("http://") or p.startswith("https://"):
        return p

    # 2. Απόλυτη διαδρομή που υπάρχει
    if os.path.isabs(p) and os.path.exists(p):
        return p

    # 3. Σχετική διαδρομή από τη ρίζα του project (π.χ. "uploads/foto.jpg")
    candidate = os.path.join(PROJECT_ROOT, p)
    if os.path.exists(candidate):
        return candidate

    # 4. Μέσα στον φάκελο uploads/ με βάση μόνο το όνομα αρχείου
    candidate = os.path.join(PROJECT_ROOT, "uploads", os.path.basename(p))
    if os.path.exists(candidate):
        return candidate

    # 5. Σχετικά με τον τρέχοντα φάκελο εκτέλεσης
    if os.path.exists(p):
        return p

    return None


# ── Φόρτωση δεδομένων ─────────────────────────────────────────────

@st.cache_data(ttl=10)
def load_problems():
    """Ανάκτηση όλων των αναφορών από τη βάση δεδομένων (ανανέωση κάθε 10 δευτερόλεπτα)."""
    return CityRepository().get_problems()

@st.cache_data(ttl=300)
def load_categories():
    """Ανάκτηση κατηγοριών από τη βάση (ανανέωση κάθε 5 λεπτά)."""
    conn = CityRepository()._get_connection()
    rows = conn.execute("SELECT * FROM category").fetchall()
    conn.close()
    return {row["id"]: row["name"] for row in rows}

@st.cache_data(ttl=300)
def load_statuses():
    """Ανάκτηση καταστάσεων από τη βάση (ανανέωση κάθε 5 λεπτά)."""
    conn = CityRepository()._get_connection()
    rows = conn.execute("SELECT * FROM status").fetchall()
    conn.close()
    return {row["id"]: row["name"] for row in rows}

# Αρχικοποίηση δεδομένων και μετατροπή σε Pandas DataFrame
problems   = load_problems()
categories = load_categories()
statuses   = load_statuses()
df = pd.DataFrame(problems)

# Εμπλουτισμός (enrichment) του DataFrame με τα ονόματα των κατηγοριών και των καταστάσεων
if not df.empty:
    df["category_id"]   = df["category_id"].astype(int)
    df["status_id"]     = df["status_id"].astype(int)
    df["category_name"] = df["category_id"].map(categories)
    df["status_name"]   = df["status_id"].map(statuses)
    df["created_at"]    = pd.to_datetime(df["created_at"])

# Πλήκτρο χειροκίνητης ανανέωσης δεδομένων στην πλευρική μπάρα (Sidebar)
if st.sidebar.button("🔄 Ανανέωση"):
    st.cache_data.clear()
    st.rerun()

st.title("📋 Διαχείριση Αναφορών")
st.divider()

# Αν δεν υπάρχουν δεδομένα, σταματάμε την εκτέλεση της σελίδας εδώ
if df.empty:
    st.warning("Δεν υπάρχουν αναφορές.")
    st.stop()

# ── Φίλτρα ────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    selected_cat = st.selectbox("Κατηγορία", ["Όλες"] + list(categories.values()))
with col2:
    selected_stat = st.selectbox("Κατάσταση", ["Όλες"] + list(statuses.values()))
with col3:
    selected_priority = st.selectbox("Προτεραιότητα", ["Όλες", "Low", "Medium", "High"])

# Εφαρμογή των επιλεγμένων φίλτρων στο αντίγραφο του DataFrame
filtered_df = df.copy()
if selected_cat != "Όλες":
    filtered_df = filtered_df[filtered_df["category_name"] == selected_cat]
if selected_stat != "Όλες":
    filtered_df = filtered_df[filtered_df["status_name"] == selected_stat]
if selected_priority != "Όλες":
    filtered_df = filtered_df[filtered_df["priority"] == selected_priority]

# Προβολή αποτελεσμάτων σε μορφή πίνακα (DataFrame)
st.write(f"Βρέθηκαν **{len(filtered_df)}** αναφορές")
st.dataframe(
    filtered_df[["ticket_id","title","category_name","status_name","priority","upvotes","created_at"]].rename(columns={
        "ticket_id":"Ticket ID","title":"Τίτλος","category_name":"Κατηγορία",
        "status_name":"Κατάσταση","priority":"Προτεραιότητα","upvotes":"Upvotes","created_at":"Ημερομηνία"
    }),
    width='stretch'# Επέκταση του πίνακα σε όλο το διαθέσιμο πλάτος
)

st.divider()

# ── Αναλυτική Προβολή ─────────────────────────────────────────────
st.subheader("🔍 Αναλυτική Προβολή")
ticket_input = st.text_input("Ticket ID", placeholder="π.χ. TK-A1B2C3")

if ticket_input:
    # Αναζήτηση της αναφοράς με βάση το Ticket ID (αγνοώντας κενά και κεφαλαία/μικρά)
    result = df[df["ticket_id"] == ticket_input.upper().strip()]
    if not result.empty:
        row = result.iloc[0]
        st.success(f"✅ {row['title']}")

        # Προβολή στοιχείων σε 2 στήλες για καλύτερη αναγνωσιμότητα
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Ticket ID:** {row['ticket_id']}")
            st.write(f"**Κατηγορία:** {row['category_name']}")
            st.write(f"**Κατάσταση:** {row['status_name']}")
            st.write(f"**Προτεραιότητα:** {row['priority']}")
            st.write(f"**Upvotes:** {row['upvotes']}")
        with col2:
            st.write(f"**Περιγραφή:** {row['description']}")
            st.write(f"**Ημερομηνία:** {row['created_at']}")
            # Εμφάνιση σχολίου διαχειριστή, εφόσον υπάρχει (όχι null/nan)
            if row.get("admin_comment")  and str(row.get("admin_comment")) != "nan":
                st.info(f"💬 {row['admin_comment']}")

        # ── Φωτογραφία Αναφοράς ───────────────────────────────────
        st.divider()
        st.subheader("🖼 Φωτογραφία Αναφοράς")
        photo = resolve_photo_path(row.get("photo_path"))
        if photo:
            st.image(photo, caption=f"Φωτογραφία για {row['ticket_id']}", width=450)
        else:
            # Έλεγχος εάν υπήρχε path στη βάση αλλά χάθηκε το αρχείο από το δίσκο
            pp = row.get("photo_path")
            if pp and str(pp).strip().lower() not in ("", "nan", "none"):
                st.warning(f"Έχει καταχωρηθεί διαδρομή φωτογραφίας, αλλά το αρχείο δεν βρέθηκε: {pp}")
            else:
                st.caption("📷 Δεν έχει επισυναφθεί φωτογραφία σε αυτή την αναφορά.")

        st.divider()

        # Εξωτερικά APIs
        lat = row.get("latitude")
        lon = row.get("longitude")

        if lat and lon:
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("🌤 Καιρός στην περιοχή")
                with st.spinner("Ανάκτηση καιρού..."):
                    weather = get_weather(lat, lon)
                st.info(weather)

            with col2:
                st.subheader("📍 Διεύθυνση")
                address = row.get("address", "Δεν βρέθηκε διεύθυνση")
            st.info(address)
        else:
            st.warning("Δεν υπάρχουν συντεταγμένες για αυτή την αναφορά.")
    else:
        st.error("Δεν βρέθηκε.")

st.divider()

# ── Αλλαγή Κατάστασης ─────────────────────────────────────────────
st.subheader("✏️ Αλλαγή Κατάστασης")
col1, col2, col3 = st.columns(3)
with col1:
    ticket_update = st.text_input("Ticket ID για ενημέρωση")
with col2:
    new_status = st.selectbox("Νέα κατάσταση", list(statuses.values()))
with col3:
    admin_comment = st.text_input("Σχόλιο admin")

if st.button("💾 Αποθήκευση", type="primary"):
    if ticket_update:
        # Εύρεση του status_id με βάση το όνομα της κατάστασης που επέλεξε ο χρήστης
        status_id = [k for k, v in statuses.items() if v == new_status][0]
        repo = CityRepository()

        # Κλήση της μεθόδου του Repository για ενημέρωση της βάσης και του status_history
        if repo.update_problem_status(ticket_update.upper().strip(), status_id, admin_comment):
            st.success("✅ Η αποθήκευση έγινε επιτυχώς!")
            st.cache_data.clear() # Καθαρισμός cache για να ανανεωθεί ο πίνακας
            time.sleep(1) # Μικρή καθυστέρηση για να προλάβει ο χρήστης να δει το μήνυμα
            st.rerun() # Επανεκκίνηση της σελίδας
        else:
            st.error("❌ Το Ticket ID δεν βρέθηκε.")
    else:
        st.warning("⚠️ Συμπληρώστε το Ticket ID.")