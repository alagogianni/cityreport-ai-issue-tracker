"""
Σενάριο Εισαγωγής Αρχικών Δεδομένων (Seeding Script)
Αυτό το αρχείο τροφοδοτεί τη βάση με 20+ ρεαλιστικές, εικονικές αναφορές 
ώστε το σύστημα να έχει δεδομένα προς προβολή και ανάλυση στο Dashboard.
Επίσης, προσομοιώνει το ιστορικό αλλαγών (για τα στατιστικά) και δημιουργεί 
δυναμικά placeholder εικόνες με χρήση της βιβλιοθήκης Pillow.
"""
import os
from app.model.problem import Problem
from app.repository import CityRepository
from PIL import Image, ImageDraw, ImageFont


# ── Βοηθητικά για τις ενδεικτικές φωτογραφίες ─────────────────────
# Χρώματα placeholder ανά κατηγορία (category_id -> RGB)
_CATEGORY_COLORS = {
    1: (193, 78, 60),    # Οδοποιία
    2: (210, 160, 40),   # Ηλεκτροφωτισμός
    3: (52, 140, 96),    # Καθαριότητα
    4: (60, 120, 72),    # Πράσινο
    5: (96, 96, 112),    # Άλλο
}
_DEFAULT_COLOR = (96, 96, 112)


def _get_font(size):
    """
    Αναζητά μια TrueType γραμματοσειρά (για σωστή υποστήριξη Ελληνικών χαρακτήρων)
    στο σύστημα. Αν δεν βρει καμία, επιστρέφει την προεπιλεγμένη του Pillow.
    """
    for path in [r"C:\Windows\Fonts\arial.ttf",
                 r"C:\Windows\Fonts\calibri.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                 "/usr/share/fonts/truetype/freefont/FreeSans.ttf"]:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


def _make_photo(path, title, color):
    """
    Δημιουργεί μια δυναμική ενδεικτική (placeholder) εικόνα JPEG,
    η οποία περιλαμβάνει τον τίτλο της αναφοράς και χρώμα βάσει κατηγορίας.
    """
    # Δημιουργία καμβά 640x420 με το χρώμα της κατηγορίας
    img = Image.new("RGB", (640, 420), color)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 320, 640, 420], fill=(0, 0, 0))
    t = title if len(title) <= 34 else title[:31] + "..."
    draw.text((25, 344), t, fill=(255, 255, 255), font=_get_font(30))
    draw.text((25, 388), "CityReport — ενδεικτική φωτογραφία",
              fill=(205, 205, 205), font=_get_font(18))
    img.save(path, "JPEG", quality=85)


def seed():
    """
    Κύρια συνάρτηση ενορχήστρωσης.
    1. Προσθέτει τα προβλήματα στη βάση.
    2. Προσομοιώνει το ιστορικό αλλαγών (Time Series).
    3. Συνδέει τα παραγόμενα IDs με τις αντίστοιχες φωτογραφίες.
    """
    repo = CityRepository()
    
    print("🚀 Ξεκινάει η τροφοδοσία δεδομένων (Seeding)...")

    # Λίστα με 22 ρεαλιστικά προβλήματα
    test_data = [
        # --- ΕΠΙΛΥΜΕΝΑ (Status 3) ---
        Problem(title="Τεράστια λακκούβα στη Συγγρού", description="Βαθιά λακκούβα στη μεσαία λωρίδα.", latitude=37.9555, longitude=23.7152, category_id=1, address="Λεωφ. Συγγρού 150", priority="High", status_id=3, upvotes=120, created_at="2025-10-10 08:00:00", admin_comment="Έγινε ασφαλτόστρωση από συνεργείο του Δήμου."),
        Problem(title="Καμένη κολώνα ΔΕΗ", description="Σκοτάδι σε όλο το τετράγωνο.", latitude=37.9830, longitude=23.7300, category_id=2, address="Ομόνοια", priority="High", status_id=3, upvotes=45, created_at="2025-11-05 19:30:00", admin_comment="Αντικατάσταση λαμπτήρα LED."),
        Problem(title="Διαρροή ΕΥΔΑΠ", description="Πλημμύρισε ο δρόμος.", latitude=37.9400, longitude=23.6500, category_id=5, address="Πασαλιμάνι", priority="High", status_id=3, upvotes=88, created_at="2025-12-12 06:15:00", admin_comment="Το κλιμάκιο επισκεύασε τον κεντρικό αγωγό."),
        Problem(title="Πεσμένο δέντρο", description="Κλαδιά κλείνουν το πεζοδρόμιο.", latitude=37.9667, longitude=23.7166, category_id=4, address="Θησείο", priority="Medium", status_id=3, upvotes=15, created_at="2026-01-20 14:00:00", admin_comment="Απομάκρυνση κορμού από την υπηρεσία πρασίνου."),

        # --- ΣΕ ΕΞΕΛΙΞΗ (Status 2) ---
        Problem(title="Ξηλωμένα πλακάκια", description="Επικίνδυνο για πεζούς.", latitude=37.9750, longitude=23.7350, category_id=1, address="Κολωνάκι", priority="Medium", status_id=2, upvotes=30, created_at="2026-02-10 11:00:00", admin_comment="Έχει γίνει παραγγελία νέων πλακιδίων."),
        Problem(title="Χαλασμένο Φανάρι", description="Αναβοσβήνει μόνο πορτοκαλί.", latitude=37.9455, longitude=23.6455, category_id=2, address="Δημοτικό Θέατρο Πειραιά", priority="High", status_id=2, upvotes=55, created_at="2026-03-01 07:45:00", admin_comment="Αναμένεται ανταλλακτικό πλακέτας."),
        Problem(title="Σπασμένος Κάδος", description="Λείπουν οι ρόδες.", latitude=37.9850, longitude=23.7600, category_id=3, address="Αμπελόκηποι", priority="Low", status_id=2, upvotes=5, created_at="2026-03-15 09:20:00", admin_comment="Προγραμματισμένη αντικατάσταση για την επόμενη εβδομάδα."),
        Problem(title="Εγκαταλελειμμένο ΙΧ", description="Σκουριασμένο Datsun χωρίς πινακίδες.", latitude=37.9550, longitude=23.7200, category_id=5, address="Νέος Κόσμος", priority="Medium", status_id=2, upvotes=22, created_at="2026-04-05 10:10:00", admin_comment="Τοποθετήθηκε αυτοκόλλητο ειδοποίησης."),

        # --- ΑΝΑΦΕΡΘΗΚΑΝ (Status 1) ---
        Problem(title="Βουνό από μπάζα", description="Κάποιος πέταξε μπάζα ανακαίνισης στο πεζοδρόμιο.", latitude=37.9900, longitude=23.7300, category_id=3, address="Κυψέλη", priority="High", status_id=1, upvotes=40, created_at="2026-04-20 08:30:00"),
        Problem(title="Σπασμένο παγκάκι", description="Λείπουν τα ξύλα.", latitude=37.9715, longitude=23.7257, category_id=4, address="Πλατεία Συντάγματος", priority="Low", status_id=1, upvotes=8, created_at="2026-04-22 17:00:00"),
        Problem(title="Διπλοπαρκαρισμένα", description="Κλείνουν τη ράμπα ΑμεΑ καθημερινά.", latitude=37.9430, longitude=23.6470, category_id=5, address="Λιμάνι Πειραιά", priority="High", status_id=1, upvotes=65, created_at="2026-05-01 12:00:00"),
        Problem(title="Ανοιχτό φρεάτιο", description="Λείπει το καπάκι, κίνδυνος ατυχήματος.", latitude=37.9780, longitude=23.7400, category_id=5, address="Λυκαβηττός", priority="High", status_id=1, upvotes=110, created_at="2026-05-05 20:15:00"),
        Problem(title="Καμένη Λάμπα", description="Σκοτεινό στενό.", latitude=37.9600, longitude=23.7000, category_id=2, address="Καλλιθέα", priority="Medium", status_id=1, upvotes=12, created_at="2026-05-10 21:00:00"),
        Problem(title="Γκράφιτι σε μνημείο", description="Βανδαλισμός αγάλματος.", latitude=37.9740, longitude=23.7330, category_id=3, address="Ακαδημίας", priority="Medium", status_id=1, upvotes=34, created_at="2026-05-12 10:45:00"),
        Problem(title="Απότιστα δέντρα", description="Ξεραίνονται τα δέντρα στο παρτέρι.", latitude=37.9500, longitude=23.6800, category_id=4, address="Μοσχάτο", priority="Low", status_id=1, upvotes=4, created_at="2026-05-13 09:00:00"),

        # --- ΑΠΟΡΡΙΦΘΗΚΑΝ (Status 4) ---
        Problem(title="Θόρυβος από μπαρ", description="Πολύ δυνατή μουσική.", latitude=37.9760, longitude=23.7150, category_id=5, address="Γκάζι", priority="Medium", status_id=4, upvotes=20, created_at="2026-01-10 23:30:00", admin_comment="Αρμοδιότητα της ΕΛ.ΑΣ, παρακαλούμε καλέστε το 100."),
        Problem(title="Ιδιωτικό οικόπεδο με χόρτα", description="Κίνδυνος πυρκαγιάς σε περιφραγμένο οικόπεδο.", latitude=37.9950, longitude=23.7400, category_id=4, address="Γαλάτσι", priority="High", status_id=4, upvotes=50, created_at="2026-03-20 13:15:00", admin_comment="Ιδιωτικός χώρος. Εστάλη πρόστιμο στον ιδιοκτήτη."),

        # --- EXTRA (Status 1) ---
        Problem(title="Σπασμένο πεζοδρόμιο", description="Ρίζες δέντρου σήκωσαν τις πλάκες.", latitude=37.9350, longitude=23.6400, category_id=1, address="Πειραϊκή", priority="Medium", status_id=1, upvotes=18, created_at="2026-05-02 16:20:00"),
        Problem(title="Λάμπες που τρεμοπαίζουν", description="Ενοχλητικό το βράδυ.", latitude=37.9880, longitude=23.7500, category_id=2, address="Γκύζη", priority="Low", status_id=1, upvotes=7, created_at="2026-05-08 19:10:00"),
        Problem(title="Μηχανάκια στο πεζοδρόμιο", description="Έχουν κλείσει όλη τη δίοδο.", latitude=37.9820, longitude=23.7310, category_id=5, address="Πανεπιστημίου", priority="High", status_id=1, upvotes=95, created_at="2026-05-11 08:50:00"),
        Problem(title="Νερά στον δρόμο", description="Μάλλον σπασμένος σωλήνας.", latitude=37.9650, longitude=23.7200, category_id=5, address="Κουκάκι", priority="Medium", status_id=1, upvotes=25, created_at="2026-05-14 07:30:00"),
        Problem(title="Σκουπίδια εκτός κάδου", description="Χαρτόκουτα πεταμένα.", latitude=37.9480, longitude=23.6550, category_id=3, address="Καστέλλα", priority="Low", status_id=1, upvotes=9, created_at="2026-05-14 10:00:00"),
    ]

    # Αποθήκευση και συλλογή πραγματικών IDs
    real_ids = []
    for p in test_data:
        repo.add_problem(p)
        # Ανάκτηση του πραγματικού ID από τη βάση (απαραίτητο για τα foreign keys)
        conn = repo._get_connection()
        row = conn.execute(
            "SELECT id FROM problem WHERE ticket_id = ?", (p.ticket_id,)
        ).fetchone()
        conn.close()
        real_ids.append(row["id"])
       
    print(f"✅ Προστέθηκαν {len(test_data)} προβλήματα!")

    # Χτίσιμο του πίνακα status_history με τα πραγματικά IDs 
    # Αυτό εξασφαλίζει ότι τα στατιστικά "Χρόνου Επίλυσης" θα δείχνουν σωστά δεδομένα
    print("⏳ Χτίζουμε το ιστορικό των αλλαγών (Time travel) για τα γραφήματα...")

    conn = repo._get_connection()
    cursor = conn.cursor()

    # Ορισμός ιστορικού με βάση τη θέση στη λίστα (0-indexed)
    # real_ids[0] = Λακκούβα, real_ids[1] = ΔΕΗ, κλπ
    history = [
        # Λακκούβα (idx 0): 1→2→3
        (real_ids[0], 1, 2, "2025-10-12 09:30:00"),
        (real_ids[0], 2, 3, "2025-10-15 14:20:00"),
        # ΔΕΗ (idx 1): 1→3
        (real_ids[1], 1, 3, "2025-11-06 11:00:00"),
        # ΕΥΔΑΠ (idx 2): 1→2→3
        (real_ids[2], 1, 2, "2025-12-12 08:00:00"),
        (real_ids[2], 2, 3, "2025-12-12 16:45:00"),
        # Δέντρο (idx 3): 1→2→3
        (real_ids[3], 1, 2, "2026-01-22 10:00:00"),
        (real_ids[3], 2, 3, "2026-01-25 13:30:00"),
        # Πλακάκια (idx 4): 1→2
        (real_ids[4], 1, 2, "2026-02-15 09:15:00"),
        # Φανάρι (idx 5): 1→2
        (real_ids[5], 1, 2, "2026-03-05 12:00:00"),
        # Κάδος (idx 6): 1→2
        (real_ids[6], 1, 2, "2026-03-20 08:00:00"),
        # Datsun (idx 7): 1→2
        (real_ids[7], 1, 2, "2026-04-20 11:30:00"),
        # Μπαρ (idx 15): 1→4
        (real_ids[15], 1, 4, "2026-01-11 09:00:00"),
        # Οικόπεδο (idx 16): 1→2→4
        (real_ids[16], 1, 2, "2026-03-25 10:00:00"),
        (real_ids[16], 2, 4, "2026-03-28 14:00:00"),
    ]

    try:
        cursor.executemany(
            "INSERT INTO status_history (problem_id, old_status_id, new_status_id, changed_at) VALUES (?, ?, ?, ?)",
            history
        )
        conn.commit()
        print("✅ Το ιστορικό καταστάσεων (Time-Series) χτίστηκε τέλεια!")
    except Exception as e:
        print(f"Σφάλμα κατά την προσθήκη ιστορικού: {e}")
    finally:
        conn.close()

    # ── Ενδεικτικές φωτογραφίες για μερικές αναφορές ──────────────
    # Δημιουργούμε placeholder εικόνες στον φάκελο uploads/ και τις
    # αναθέτουμε στις 6 πρώτες αναφορές, ώστε να φαίνεται η λειτουργία
    # "προβολή φωτογραφιών" στο dashboard.
    print("🖼  Δημιουργία ενδεικτικών φωτογραφιών...")
    os.makedirs("uploads", exist_ok=True)
    photo_indices = [0, 1, 2, 3, 4, 5]

    conn = repo._get_connection()
    try:
        for i in photo_indices:
            p = test_data[i]
            color = _CATEGORY_COLORS.get(p.category_id, _DEFAULT_COLOR)
            fname = f"{p.ticket_id}.jpg"
            fpath = os.path.join("uploads", fname)
            _make_photo(fpath, p.title, color)
            conn.execute(
                "UPDATE problem SET photo_path = ? WHERE id = ?",
                (f"uploads/{fname}", real_ids[i])
            )
        conn.commit()
        print(f"Προστέθηκαν {len(photo_indices)} ενδεικτικές φωτογραφίες στον φάκελο 'uploads/'.")
    except Exception as e:
        print(f"Σφάλμα κατά τη δημιουργία φωτογραφιών: {e}")
    finally:
        conn.close()

    print("Η βάση είναι έτοιμη για Dashboarding!")


if __name__ == "__main__":
    seed()