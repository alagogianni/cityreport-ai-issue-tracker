
"""
Κεντρικό Αρχείο Εκκίνησης (Entry Point) του REST API (Backend).
Αυτό το αρχείο αναλαμβάνει να εκκινήσει τον εξυπηρετητή (server) του Flask,
ώστε να αρχίσει να δέχεται τα αιτήματα (HTTP requests) των πολιτών.
"""
import os

# Εισαγωγή της ήδη ρυθμισμένης εφαρμογής Flask από το αρχείο των διαδρομών (routes)
from src.api.routes import app

if __name__ == "__main__":
    # Το debug ανοίγει μόνο αν ορίσεις FLASK_DEBUG=1, αλλιώς μένει κλειστό
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    print("🚀 Ο Server ξεκινάει! Περιμένει αναφορές στο http://127.0.0.1:5000")
    app.run(debug=debug, host="0.0.0.0", port=5000)