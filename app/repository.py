import sqlite3
import os
from app.model.problem import Problem

class CityRepository:
    def __init__(self):
        """
        Αρχικοποιεί το αποθετήριο (repository) και ορίζει τη διαδρομή (path) 
        προς τη βάση δεδομένων SQLite του συστήματος (cityreport.db).
        Η διαδρομή υπολογίζεται δυναμικά με βάση τη θέση αυτού του αρχείου.
        """
        self.db_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'database', 'cityreport.db')
    def _get_connection(self):
        """
        Ιδιωτική (private) βοηθητική μέθοδος για τη δημιουργία σύνδεσης με τη βάση.
        Χρησιμοποιεί το sqlite3.Row ώστε οι γραμμές (rows) που επιστρέφει η βάση 
        να συμπεριφέρονται ως λεξικά (dictionary-like objects) αντί για απλές πλειάδες.
        """
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        return conn

    def get_problems(self):
        """
        Ανακτά όλες τις αναφορές προβλημάτων από τη βάση δεδομένων.
        Επιστρέφει μια λίστα από λεξικά (dictionaries) με τα δεδομένα των προβλημάτων.
        """
        conn = self._get_connection()
        rows = conn.execute("SELECT * FROM problem").fetchall()
        conn.close()
        
        return [dict(row) for row in rows]

    def add_problem(self, problem: Problem):
        """
        Εισάγει μια νέα αναφορά προβλήματος (αντικείμενο Problem) στη βάση δεδομένων.
        Επιστρέφει True αν η εγγραφή πέτυχε, αλλιώς False.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        query = """
            INSERT INTO problem 
            (ticket_id, title, description, latitude, longitude, address, photo_path, 
             category_id, status_id, priority, upvotes, admin_comment, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        values = (
            problem.ticket_id, problem.title, problem.description,
            float(problem.latitude), float(problem.longitude),
            problem.address, problem.photo_path, problem.category_id,
            problem.status_id, problem.priority, problem.upvotes,
            problem.admin_comment, problem.created_at # <--- Προσθήκη ημερομηνίας
        )
        
        
        try:
            cursor.execute(query, values)
            conn.commit()
            print(f"Η αναφορά αποθηκεύτηκε με Ticket ID: {problem.ticket_id}")
            return True
        except sqlite3.Error as e:
            print(f"Σφάλμα κατά την εγγραφή: {e}")
            return False
        finally:
            conn.close()

    def upvote_problem(self, problem_id):
        """
        Αυξάνει τον μετρητή θετικών ψήφων (upvotes) ενός συγκεκριμένου προβλήματος κατά 1.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = "UPDATE problem SET upvotes = upvotes + 1 WHERE id = ?"
        
        try:
            cursor.execute(query, (problem_id,))
            conn.commit()
            print(f"Το πρόβλημα #{problem_id} πήρε ένα upvote!")
        except sqlite3.Error as e:
            print(f"Σφάλμα κατά το upvote: {e}")
        finally:
            conn.close()


    def update_photo_path(self, ticket_id, photo_path):
        """
        Ενημερώνει τη διαδρομή (path) της φωτογραφίας για μια υπάρχουσα αναφορά.
        Ενημερώνει επίσης το πεδίο updated_at με την τρέχουσα τοπική ώρα.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE problem SET photo_path = ?, updated_at = datetime('now', 'localtime') WHERE ticket_id = ?",
                (photo_path, ticket_id.upper().strip())
            )
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Σφάλμα κατά ενημέρωση φωτογραφίας: {e}")
            return False
        finally:
            conn.close()

    def update_problem_status(self, ticket_id, new_status_id, admin_comment=None):
        """
        Ενημερώνει την κατάσταση (status) ενός προβλήματος και προαιρετικά προσθέτει σχόλιο διαχειριστή.
        Παράλληλα, καταγράφει αυτόματα την αλλαγή στον πίνακα ιστορικού (status_history).
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # 1. Βρίσκουμε το ID του προβλήματος και το παλιό status από το ticket_id
            normalized_id = ticket_id.upper().strip()
            problem = cursor.execute("SELECT id, status_id FROM problem WHERE ticket_id = ?", (normalized_id,)).fetchone()
            if not problem:
                return False # Δεν βρέθηκε

            problem_id = problem['id']
            old_status_id = problem['status_id']

            # 2. Ενημερώνουμε τον κύριο πίνακα problem με τη νέα κατάσταση
            cursor.execute("""
                UPDATE problem
                SET status_id = ?, admin_comment = ?, updated_at = datetime('now', 'localtime')
                WHERE id = ?
            """, (new_status_id, admin_comment, problem_id))
            
            # 3. Εάν άλλαξε η κατάσταση, προσθέτουμε την καταγραφή στο status_history!
            if old_status_id != new_status_id:
                cursor.execute("""
                    INSERT INTO status_history (problem_id, old_status_id, new_status_id, changed_at, comment) 
                    VALUES (?, ?, ?, datetime('now', 'localtime'), ?)
                """, (problem_id, old_status_id, new_status_id, admin_comment))
                
            conn.commit()
            return True
        except Exception as e:
            print(f"Σφάλμα: {e}")
            return False
        finally:
            conn.close()


    def get_problem_by_ticket(self, ticket_id):
        """Ανακτά μια αναφορά βάσει του ticket_id της."""
        conn = self._get_connection()
        try:
            problem = conn.execute(
                "SELECT * FROM problem WHERE ticket_id = ?",
                (ticket_id.upper().strip(),)
            ).fetchone()
            return dict(problem) if problem else None
        finally:
            conn.close()

    def update_description(self, ticket_id, new_description):
        """Ενημερώνει την περιγραφή μιας αναφοράς βάσει ticket_id."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE problem SET description = ?, updated_at = datetime('now', 'localtime') WHERE ticket_id = ?",
                (new_description, ticket_id.upper().strip())
            )
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Σφάλμα κατά ενημέρωση περιγραφής: {e}")
            return False
        finally:
            conn.close()


    def find_duplicate(self, title, latitude, longitude):
        """
        Αναζητά ένα ήδη καταχωρημένο πρόβλημα με τον ίδιο ακριβώς τίτλο και παρόμοια τοποθεσία.
        Η απόκλιση (ABS < 0.001) στις συντεταγμένες αντιστοιχεί σε ακτίνα περίπου 100 μέτρων.
        Επιστρέφει τα βασικά στοιχεία του προβλήματος αν βρεθεί, αλλιώς None.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        result = cursor.execute("""
            SELECT id, ticket_id, upvotes FROM problem 
            WHERE title = ? 
            AND ABS(latitude - ?) < 0.001 
            AND ABS(longitude - ?) < 0.001
            LIMIT 1
        """, (title, latitude, longitude)).fetchone()
        conn.close()
        return dict(result) if result else None

# --- ΔΟΚΙΜΕΣ---
if __name__ == "__main__":
    # 1. Έλεγχος Σύνδεσης με τη βάση
    repo = CityRepository()
    
    # 2. Έλεγχος Ανάγνωσης υφιστάμενων δεδομένων
    data_before = repo.get_problems()
    
    # 3. Έλεγχος Προσθήκης (Δημιουργούμε ένα εικονικό αντικείμενο Problem για δοκιμή)
    # Προσοχή: Βάλαμε category_id=2 (π.χ. Ηλεκτροφωτισμός)
    # Προσοχή: Βάλαμε category_id=2 (Ηλεκτροφωτισμός)
    test_issue = Problem(
        title="Φωτισμός", 
        description="Καμένη λάμπα", 
        latitude=37.9, 
        longitude=23.7, 
        category_id=2, 
        address="Οδός Τεστ 1", 
        priority="Low"
    )
    repo.add_problem(test_issue)
    
    # 4. Έλεγχος Ανάγνωσης μετά την εισαγωγή
    data_after = repo.get_problems()
    
    print("Repository Test Done!")