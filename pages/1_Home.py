"""
Αρχική Σελίδα (Home) - Admin Dashboard (Streamlit)
Παρέχει μια γρήγορη επισκόπηση (overview) των συνολικών προβλημάτων της πόλης
μέσω KPIs (metrics) και βασικών γραφημάτων.
"""
import streamlit as st
import pandas as pd
import sys, os
# Προσθήκη του ριζικού φακέλου στο sys.path για να μπορεί να κάνει import τα modules του app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.repository import CityRepository

# Χρήση προσωρινής μνήμης (caching) για τη βελτιστοποίηση της απόδοσης.
# Τα προβλήματα ανανεώνονται αυτόματα κάθε 10 δευτερόλεπτα (ttl=10).
@st.cache_data(ttl=10)
def load_problems():
    """Ανάκτηση όλων των αναφορών από το αποθετήριο."""
    return CityRepository().get_problems()

# Οι κατηγορίες και οι καταστάσεις σπάνια αλλάζουν, οπότε τις κρατάμε στη μνήμη για 5 λεπτά (ttl=300).
@st.cache_data(ttl=300)
def load_categories():
    """Ανάκτηση και μετατροπή των κατηγοριών σε λεξικό (id -> name)."""
    conn = CityRepository()._get_connection()
    rows = conn.execute("SELECT * FROM category").fetchall()
    conn.close()
    return {row["id"]: row["name"] for row in rows}

@st.cache_data(ttl=300)
def load_statuses():
    """Ανάκτηση και μετατροπή των καταστάσεων σε λεξικό (id -> name)."""
    conn = CityRepository()._get_connection()
    rows = conn.execute("SELECT * FROM status").fetchall()
    conn.close()
    return {row["id"]: row["name"] for row in rows}

# Φόρτωση των δεδομένων
problems   = load_problems()
categories = load_categories()
statuses   = load_statuses()

# Μετατροπή της λίστας λεξικών σε Pandas DataFrame για εύκολη ανάλυση και χειρισμό
df = pd.DataFrame(problems)

# Εμπλουτισμός (enrichment) του DataFrame με ονόματα κατηγοριών και καταστάσεων
if not df.empty:
    df["category_id"]   = df["category_id"].astype(int)
    df["status_id"]     = df["status_id"].astype(int)
    # Χρήση της μεθόδου map() του Pandas για αντικατάσταση των IDs με τα αναγνώσιμα ονόματα
    df["category_name"] = df["category_id"].map(categories)
    df["status_name"]   = df["status_id"].map(statuses)
    # Μετατροπή της στήλης created_at σε αντικείμενο datetime για σωστή χρονική ταξινόμηση
    df["created_at"]    = pd.to_datetime(df["created_at"])

# Πλήκτρο χειροκίνητης ανανέωσης στην πλευρική μπάρα (Sidebar)
if st.sidebar.button("🔄 Ανανέωση"):
    st.cache_data.clear()
    st.rerun()

# --- Διεπαφή Χρήστη (UI) ---
st.title("🏠 Αρχική")
st.divider()

# Υπολογισμός των βασικών δεικτών (KPIs)
total    = len(df)
open_    = len(df[df["status_name"] == "Αναφέρθηκε"]) if not df.empty else 0
progress = len(df[df["status_name"] == "Σε Εξέλιξη"]) if not df.empty else 0
solved   = len(df[df["status_name"] == "Επιλύθηκε"])  if not df.empty else 0

# Προβολή των KPIs σε 4 ισομεγέθεις στήλες
col1, col2, col3, col4 = st.columns(4)
col1.metric("📁 Σύνολο", total)
col2.metric("🟡 Αναφέρθηκε", open_)
col3.metric("🔵 Σε Εξέλιξη", progress)
col4.metric("🟢 Επιλύθηκε", solved)

st.divider()

# Δημιουργία Γραφημάτων
if not df.empty:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Αναφορές ανά Κατηγορία")
        # Καταμέτρηση των εμφανίσεων κάθε κατηγορίας και μετονομασία των στηλών
        cnt = df["category_name"].value_counts().reset_index()
        cnt.columns = ["Κατηγορία", "Πλήθος"]
        # Χρήση του εγγενούς bar_chart του Streamlit
        st.bar_chart(cnt.set_index("Κατηγορία"))
    with col2:
        st.subheader("Αναφορές ανά Κατάσταση")
        cnt2 = df["status_name"].value_counts().reset_index()
        cnt2.columns = ["Κατάσταση", "Πλήθος"]
        st.bar_chart(cnt2.set_index("Κατάσταση"))
