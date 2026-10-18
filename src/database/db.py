import sqlite3
import os

# Ορισμός της απόλυτης διαδρομής για το αρχείο της βάσης δεδομένων (cityreport.db)
DB_PATH = os.path.join(os.path.dirname(__file__), 'cityreport.db')

def get_db_connection():
    """
    Δημιουργεί και επιστρέφει μια σύνδεση με τη βάση δεδομένων SQLite.
    """
    conn = sqlite3.connect(DB_PATH)

    # Ενεργοποίηση των Foreign Keys, καθώς στην SQLite είναι από προεπιλογή απενεργοποιημένα.
    # Απαραίτητο για να λειτουργούν σωστά οι σχέσεις ON DELETE CASCADE / RESTRICT.
    conn.execute("PRAGMA foreign_keys = ON;")

    # Ρύθμιση ώστε οι εγγραφές (rows) να επιστρέφονται ως αντικείμενα τύπου dictionary
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Αρχικοποιεί το σχήμα της βάσης δεδομένων. Δημιουργεί τους απαραίτητους 
    πίνακες (εφόσον δεν υπάρχουν ήδη) και εισάγει τα αρχικά δεδομένα (seeding).
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Πίνακας κατηγοριών (category)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS category (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    # 2. Πίνακας καταστάσεων (status) 
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    # 3. Πίνακας αναφορών προβλημάτων (problem)
    # Περιλαμβάνει Ξένα Κλειδιά (Foreign Keys) για την κατηγορία και την κατάσταση, 
    # καθώς και περιορισμό ελέγχου (CHECK) για τις τιμές της προτεραιότητας.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS problem (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            description TEXT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            address TEXT,
            photo_path TEXT,
            category_id INTEGER NOT NULL,
            status_id INTEGER DEFAULT 1,
            priority TEXT DEFAULT 'Medium',
            upvotes INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT (datetime('now', 'localtime')),
            updated_at DATETIME DEFAULT (datetime('now', 'localtime')),
            admin_comment TEXT,
            FOREIGN KEY (category_id) REFERENCES category (id) ON DELETE RESTRICT,
            FOREIGN KEY (status_id) REFERENCES status (id) ON DELETE RESTRICT,
            CHECK (priority IN ('Low', 'Medium', 'High'))
        )
    ''')

    # 4. Πίνακας ιστορικού καταστάσεων (status_history)
    # Καταγράφει πότε και πώς άλλαξε κατάσταση ένα πρόβλημα. 
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS status_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            problem_id INTEGER NOT NULL,
            old_status_id INTEGER NOT NULL,
            new_status_id INTEGER NOT NULL,
            changed_at DATETIME DEFAULT (datetime('now', 'localtime')),
            comment TEXT,
            FOREIGN KEY (problem_id) REFERENCES problem (id) ON DELETE CASCADE,
            FOREIGN KEY (old_status_id) REFERENCES status (id),
            FOREIGN KEY (new_status_id) REFERENCES status (id)
        )
    ''')


    # --- Εισαγωγή Αρχικών Δεδομένων (Seeding) ---

     #Προκαθορισμένες κατηγορίες προβλημάτων για το σύστημα
    category = ['Οδοποιία', 'Ηλεκτροφωτισμός', 'Καθαριότητα', 'Πράσινο', 'Άλλο']
    for cat in category:
        # Χρήση INSERT OR IGNORE για να μην υπάρξει σφάλμα (Unique Constraint) αν το script τρέξει 2η φορά
        cursor.execute('INSERT OR IGNORE INTO category (name) VALUES (?)', (cat,))

    # Προκαθορισμένες καταστάσεις ροής εργασιών (workflow)
    status = ['Αναφέρθηκε', 'Σε Εξέλιξη', 'Επιλύθηκε', 'Απορρίφθηκε']
    for stat in status:
        cursor.execute('INSERT OR IGNORE INTO status (name) VALUES (?)', (stat,))

    # Αποθήκευση αλλαγών και κλείσιμο σύνδεσης
    conn.commit()
    conn.close()
    print(f"Database initialized successfully at:{DB_PATH}")

# Το μπλοκ αυτό εκτελείται μόνο όταν το αρχείο τρέξει απευθείας (ως script)
if __name__ == "__main__":
    init_db()


    

