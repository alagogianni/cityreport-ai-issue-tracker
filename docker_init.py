
"""
Σενάριο Αρχικοποίησης και Εισαγωγής Δεδομένων (Setup & Seeding Script)
Αυτό το αρχείο διαχειρίζεται την αυτόματη δημιουργία της βάσης δεδομένων
και την εισαγωγή των αρχικών (εικονικών) αναφορών που απαιτεί η εργασία,
αποτρέποντας την προσθήκη διπλότυπων δεδομένων αν η βάση έχει ήδη δεδομένα.
"""
import sqlite3
import subprocess
import sys

# Ορισμός της διαδρομής της βάσης δεδομένων
DB_PATH = "src/database/cityreport.db"

# Εκτέλεση του db.py ως εξωτερική διεργασία (subprocess)
# Χρησιμοποιεί το sys.executable για να διασφαλίσει ότι χρησιμοποιείται 
# το ίδιο περιβάλλον Python. Το check=True διακόπτει το script αν υπάρξει σφάλμα.
subprocess.run([sys.executable, "src/database/db.py"], check=True)

need_seed = True
try:
    # Σύνδεση στη βάση για να ελέγξουμε αν υπάρχουν ήδη καταχωρημένα προβλήματα
    conn = sqlite3.connect(DB_PATH)
    count = conn.execute("SELECT COUNT(*) FROM problem").fetchone()[0]
    conn.close()

    # Αν το πλήθος (count) είναι 0, η βάση είναι άδεια και χρειάζεται seeding
    need_seed = (count == 0)
except Exception:
    # Αν υπάρξει οποιοδήποτε σφάλμα (π.χ. δεν βρέθηκε ο πίνακας), 
    # θεωρούμε ότι η βάση χρειάζεται seeding
    need_seed = True

# Αν η βάση είναι άδεια, εκτελούμε το αρχείο εισαγωγής εικονικών δεδομένων (seed_data.py)
if need_seed:
    print("Empty DB - running seed_data.py ...", flush=True)
    subprocess.run([sys.executable, "seed_data.py"], check=True)
else:
    # Αν η βάση έχει ήδη δεδομένα, παρακάμπτουμε το seeding για να μην υπάρχουν διπλότυπα
    print("DB already has data - skipping seed.", flush=True)
