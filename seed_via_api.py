"""
seed_via_api.py
---------------
Καταχώρηση 22 εικονικών αναφορών μαζικά μέσω του REST API.
Προϋπόθεση: το Flask API πρέπει να τρέχει στο http://localhost:5000

Εκτέλεση:
    python seed_via_api.py
"""

import requests

API_URL = "http://localhost:5000/api/problems"

# 22 εικονικές αναφορές — διαφορετικές από το seed_data.py
# Καλύπτουν διαφορετικές κατηγορίες και περιοχές
problems = [
    {
        "title": "Λακκούβα στην Πατησίων",
        "description": "Μεγάλη λακκούβα στη δεξιά λωρίδα, επικίνδυνη για μοτοσικλέτες.",
        "latitude": 37.9950,
        "longitude": 23.7280
    },
    {
        "title": "Σβηστά φώτα σε διάβαση πεζών",
        "description": "Τα φώτα της διάβασης δεν λειτουργούν εδώ και μια εβδομάδα.",
        "latitude": 37.9720,
        "longitude": 23.7410
    },
    {
        "title": "Σκουπίδια στην παραλία",
        "description": "Μεγάλη ποσότητα σκουπιδιών έχει συσσωρευτεί στην παραλία.",
        "latitude": 37.9280,
        "longitude": 23.6900
    },
    {
        "title": "Ξερά δέντρα στο άλσος",
        "description": "Αρκετά δέντρα στο άλσος φαίνονται ξερά και κινδυνεύουν να πέσουν.",
        "latitude": 37.9810,
        "longitude": 23.7180
    },
    {
        "title": "Χαλασμένος φωτεινός σηματοδότης",
        "description": "Το φανάρι στη διασταύρωση δείχνει ταυτόχρονα κόκκινο και πράσινο.",
        "latitude": 37.9640,
        "longitude": 23.7050
    },
    {
        "title": "Υπερχείλιση κάδων στην αγορά",
        "description": "Οι κάδοι στη λαϊκή αγορά είναι γεμάτοι και δεν έχουν αδειαστεί.",
        "latitude": 37.9870,
        "longitude": 23.7490
    },
    {
        "title": "Εγκαταλελειμμένο φορτηγό",
        "description": "Παλιό φορτηγό χωρίς πινακίδες μπλοκάρει τον δρόμο εδώ και μέρες.",
        "latitude": 37.9530,
        "longitude": 23.7080
    },
    {
        "title": "Σπασμένος αγωγός στην Κηφισιά",
        "description": "Νερό τρέχει στον δρόμο από σπασμένο αγωγό της ΕΥΔΑΠ.",
        "latitude": 38.0730,
        "longitude": 23.8100
    },
    {
        "title": "Επικίνδυνη στροφή χωρίς σήμανση",
        "description": "Απότομη στροφή χωρίς καθόλου σήμανση, έχουν γίνει ήδη ατυχήματα.",
        "latitude": 37.9420,
        "longitude": 23.6620
    },
    {
        "title": "Βανδαλισμός παιδικής χαράς",
        "description": "Έχουν σπάσει οι κούνιες και η τσουλήθρα στην παιδική χαρά.",
        "latitude": 37.9680,
        "longitude": 23.7230
    },
    {
        "title": "Λακκούβα στη Λεωφόρο Αλεξάνδρας",
        "description": "Βαθιά λακκούβα κοντά στο πεζοδρόμιο που δυσκολεύει τους πεζούς.",
        "latitude": 37.9860,
        "longitude": 23.7370
    },
    {
        "title": "Μολυσμένο ρέμα",
        "description": "Αποχετευτικά απόβλητα ρέουν στο ρέμα, έντονη δυσοσμία.",
        "latitude": 38.0120,
        "longitude": 23.7650
    },
    {
        "title": "Σπασμένο κιγκλίδωμα σε γέφυρα",
        "description": "Το κιγκλίδωμα ασφαλείας στη γέφυρα είναι σπασμένο, κίνδυνος για πεζούς.",
        "latitude": 37.9590,
        "longitude": 23.6980
    },
    {
        "title": "Παράνομη χωματερή",
        "description": "Κάποιοι έχουν δημιουργήσει παράνομη χωματερή σε κενό οικόπεδο.",
        "latitude": 38.0050,
        "longitude": 23.7820
    },
    {
        "title": "Καμένος φωτιστής σε πάρκο",
        "description": "Ο μοναδικός φωτιστής στο πάρκο είναι καμένος, επικίνδυνο τις νύχτες.",
        "latitude": 37.9750,
        "longitude": 23.7120
    },
    {
        "title": "Ρωγμές στο οδόστρωμα",
        "description": "Μεγάλες ρωγμές στο οδόστρωμα που μεγαλώνουν μετά από κάθε βροχή.",
        "latitude": 37.9910,
        "longitude": 23.7560
    },
    {
        "title": "Αδέσποτα σκυλιά σε πάρκο",
        "description": "Αγέλη αδέσποτων σκύλων στο πάρκο που απειλούν τους επισκέπτες.",
        "latitude": 37.9470,
        "longitude": 23.6730
    },
    {
        "title": "Πλημμυρισμένη υπόγεια διάβαση",
        "description": "Η υπόγεια διάβαση είναι πλημμυρισμένη μετά τις βροχές.",
        "latitude": 37.9830,
        "longitude": 23.7440
    },
    {
        "title": "Σπασμένος κρουνός άρδευσης",
        "description": "Κρουνός άρδευσης στο πάρκο τρέχει συνέχεια, σπατάλη νερού.",
        "latitude": 37.9620,
        "longitude": 23.7190
    },
    {
        "title": "Γκράφιτι σε σχολείο",
        "description": "Βανδαλισμός με γκράφιτι στον εξωτερικό τοίχο του δημοτικού σχολείου.",
        "latitude": 37.9760,
        "longitude": 23.7320
    },
    {
        "title": "Κατεστραμμένο πεζοδρόμιο στο Μαρούσι",
        "description": "Το πεζοδρόμιο έχει καταστραφεί από ρίζες δέντρων, αδύνατο να περάσει αμαξίδιο.",
        "latitude": 38.0500,
        "longitude": 23.8050
    },
    {
        "title": "Έλλειψη σήμανσης σε εργοτάξιο",
        "description": "Εργοτάξιο στη μέση του δρόμου χωρίς καθόλου σήμανση ή φώτα.",
        "latitude": 37.9690,
        "longitude": 23.7260
    },
]


def seed():
    print(f"Ξεκινάει η καταχώρηση {len(problems)} αναφορών μέσω REST API...")
    print(f"API URL: {API_URL}\n")

    success = 0
    failed = 0

    for i, problem in enumerate(problems, 1):
        try:
            response = requests.post(API_URL, json=problem, timeout=15)

            if response.status_code in (200, 201):
                data = response.json()
                ticket = data.get("ticket_id", "-")
                category = data.get("auto_category_id", "-")
                priority = data.get("auto_priority", "-")
                print(f"  [{i:02d}] {problem['title'][:40]:<40} -> {ticket} | cat:{category} | {priority}")
                success += 1
            else:
                print(f"  [{i:02d}] {problem['title'][:40]:<40} -> HTTP {response.status_code}: {response.text[:80]}")
                failed += 1

        except requests.exceptions.ConnectionError:
            print(f"\nΣφάλμα σύνδεσης! Βεβαιώσου οτι το Flask API τρεχει στο {API_URL}")
            print("   Εκτελεσε πρωτα: python run.py")
            return
        except Exception as e:
            print(f"  [{i:02d}] {problem['title']}: {e}")
            failed += 1

    print(f"\nΟλοκληρωθηκε! {success} επιτυχεις | {failed} αποτυχιες")


if __name__ == "__main__":
    seed()
