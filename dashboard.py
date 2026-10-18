
"""
Κεντρικό Αρχείο Εκκίνησης Dashboard (Admin Dashboard - Streamlit)
Αυτό το αρχείο αποτελεί το σημείο εισόδου (entry point) για τη διεπαφή των διαχειριστών.
Χρησιμοποιεί τη σύγχρονη λειτουργία εγγενούς πλοήγησης (st.navigation) του Streamlit 
για την υποστήριξη εφαρμογής πολλαπλών σελίδων (multipage app).
"""
import streamlit as st

# Ρύθμιση της κεντρικής σελίδας του Dashboard (πρέπει υποχρεωτικά να είναι η πρώτη εντολή Streamlit)
st.set_page_config(
    page_title="CityReport Admin",
    page_icon="🏙️",
    layout="wide"
)

# Ορισμός της πλοήγησης (Πλευρικό Μενού) και διασύνδεση με τα επιμέρους αρχεία του φακέλου pages/
pg = st.navigation([
    st.Page("pages/1_Home.py",       title="Αρχική",      icon="🏠"),
    st.Page("pages/2_Reports.py",    title="Αναφορές",    icon="📋"),
    st.Page("pages/3_Statistics.py", title="Στατιστικά",  icon="📊")
])

# Εκτέλεση και προβολή της επιλεγμένης σελίδας
pg.run()
