import uuid
from datetime import datetime

class Problem:
    def __init__(self, title, description, latitude, longitude, category_id, 
                 address=None, photo_path=None, priority="Medium", 
                 status_id=1, upvotes=0, admin_comment=None, id=None, ticket_id=None, created_at=None):
        """
        Κατασκευαστής (Constructor) της κλάσης Problem.
        Αρχικοποιεί μια νέα αναφορά προβλήματος. Εάν δεν δοθεί συγκεκριμένο Ticket ID 
        (όπως συμβαίνει συνήθως στις νέες αναφορές πολιτών), δημιουργεί αυτόματα ένα μοναδικό.
        """
        self.id = id 
        # Δημιουργία τυχαίου Ticket ID π.χ. "TK-A1B2C3" αν δεν υπάρχει ήδη
        self.ticket_id = ticket_id if ticket_id else f"TK-{uuid.uuid4().hex[:6].upper()}"
        
        self.title = title
        self.description = description
        self.latitude = latitude
        self.longitude = longitude
        self.category_id = category_id
        self.address = address
        self.photo_path = photo_path
        self.priority = priority
        self.status_id = status_id
        self.upvotes = upvotes
        self.admin_comment = admin_comment
        # Καταγραφή της τρέχουσας ώρας/ημερομηνίας αν δεν έχει παρασχεθεί (π.χ. από τη βάση)
        self.created_at = created_at if created_at else datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def __str__(self):
        """
        Επιστρέφει μια αναπαράσταση του αντικειμένου Problem σε μορφή συμβολοσειράς (string).
        Χρησιμεύει κυρίως για σκοπούς debugging και logging.
        """
        return f"Problem: {self.title} (Ticket: {self.ticket_id})"

    def to_dict(self):
        """
        Μετατρέπει τις ιδιότητες (attributes) του αντικειμένου σε λεξικό (dictionary).
        Αυτό είναι απαραίτητο στο Backend (Flask), ώστε να μπορεί να σειριοποιηθεί 
        το αντικείμενο και να επιστραφεί ως JSON response μέσω του REST API.
        """
        return {
            "id": self.id,
            "ticket_id": self.ticket_id,
            "title": self.title,
            "description": self.description,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "category_id": self.category_id,
            "address": self.address,
            "photo_path": self.photo_path,
            "priority": self.priority,
            "status_id": self.status_id,
            "upvotes": self.upvotes,
            "admin_comment": self.admin_comment,
            "created_at": self.created_at
        }

    def from_dict(self, data):
        """
        Ενημερώνει τις ιδιότητες του αντικειμένου με βάση τα δεδομένα ενός 
        παρεχόμενου λεξικού (dictionary). Χρησιμεύει για μαζική ενημέρωση πεδίων
        (π.χ. όταν λαμβάνουμε JSON δεδομένα από ένα PUT/PATCH request).
        """
        self.id = data.get("id", self.id)
        self.ticket_id = data.get("ticket_id", self.ticket_id)
        self.title = data.get("title", self.title)
        self.description = data.get("description", self.description)
        self.latitude = data.get("latitude", self.latitude)
        self.longitude = data.get("longitude", self.longitude)
        self.category_id = data.get("category_id", self.category_id)
        self.address = data.get("address", self.address)
        self.photo_path = data.get("photo_path", self.photo_path)
        self.priority = data.get("priority", self.priority)
        self.status_id = data.get("status_id", self.status_id)
        self.upvotes = data.get("upvotes", self.upvotes)
        self.admin_comment = data.get("admin_comment", self.admin_comment)

# --- ΤΕΛΟΣ ΤΗΣ ΚΛΑΣΗΣ ---

if __name__ == "__main__":
    # ΕΛΕΓΧΟΣ ΚΛΑΣΗΣ
    # Βάζουμε category_id=1 (π.χ. Οδοποιία) για να δούμε αν δουλεύει σωστά η αρχικοποίηση
    p = Problem(title="Λακκούβα", description="Μεγάλη", latitude=37.9, longitude=23.7, category_id=1)
    
    # ΕΛΕΓΧΟΣ ΣΥΝΑΡΤΗΣΗΣ to_dict() για επαλήθευση της μετατροπής σε JSON format
    result = p.to_dict()
    
    print("Τεστ ολοκληρώθηκε! Το αποτέλεσμα είναι:")
    print(result)