"""
Σελίδα Στατιστικών (Statistics) - Υποσύστημα Ανάλυσης Δεδομένων
Παρουσιάζει στατιστικά στοιχεία, διαγράμματα, γεωχωρική ανάλυση (χάρτες) 
και μετρήσεις απόδοσης (π.χ. χρόνοι επίλυσης) χρησιμοποιώντας Pandas και Plotly.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import sys, os

# Προσθήκη του ριζικού φακέλου στο sys.path για την εισαγωγή των τοπικών modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.repository import CityRepository

# ── Συναρτήσεις Φόρτωσης Δεδομένων (με Caching) ───────────────────

@st.cache_data(ttl=10)
def load_problems():
    """Ανάκτηση όλων των προβλημάτων από τη βάση δεδομένων."""
    return CityRepository().get_problems()

@st.cache_data(ttl=300)
def load_categories():
    """Ανάκτηση των κατηγοριών και δημιουργία λεξικού (id -> name)."""
    conn = CityRepository()._get_connection()
    rows = conn.execute("SELECT * FROM category").fetchall()
    conn.close()
    return {row["id"]: row["name"] for row in rows}

@st.cache_data(ttl=300)
def load_statuses():
    """Ανάκτηση των καταστάσεων και δημιουργία λεξικού (id -> name)."""
    conn = CityRepository()._get_connection()
    rows = conn.execute("SELECT * FROM status").fetchall()
    conn.close()
    return {row["id"]: row["name"] for row in rows}

@st.cache_data(ttl=10)
def load_resolution_times():
    """
    Υπολογίζει τον μέσο χρόνο επίλυσης ανά κατηγορία, χρησιμοποιώντας 
    τον πίνακα status_history.
    Αναζητά εγγραφές όπου η κατάσταση άλλαξε σε 'Επιλύθηκε' (new_status_id = 3).
    """
    conn = CityRepository()._get_connection()
    query = """
    SELECT 
        p.id,
        c.name AS category_name,
        sh.changed_at AS resolved_at,
        p.created_at
    FROM status_history sh
    JOIN problem p ON sh.problem_id = p.id
    JOIN category c ON p.category_id = c.id
    WHERE sh.new_status_id = 3
"""
    rows = conn.execute(query).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ── Φόρτωση δεδομένων ─────────────────────────────────────────────
problems   = load_problems()
categories = load_categories()
statuses   = load_statuses()

# Μετατροπή σε Pandas DataFrame για εύκολη ανάλυση
df = pd.DataFrame(problems)

if not df.empty:
    # Μετατροπή τύπων δεδομένων και αντιστοίχιση (mapping) ονομάτων
    df["category_id"]   = df["category_id"].astype(int)
    df["status_id"]     = df["status_id"].astype(int)
    df["category_name"] = df["category_id"].map(categories)
    df["status_name"]   = df["status_id"].map(statuses)
    df["created_at"]    = pd.to_datetime(df["created_at"])

# Πλήκτρο χειροκίνητης ανανέωσης
if st.sidebar.button("🔄 Ανανέωση"):
    st.cache_data.clear()
    st.rerun()

st.title("📊 Στατιστικά & Ανάλυση")
st.divider()

if df.empty:
    st.warning("Δεν υπάρχουν δεδομένα.")
    st.stop()

# ── Δημιουργία Καρτελών (Tabs) για οργάνωση του περιεχομένου ──────
tab1, tab2, tab3, tab4 = st.tabs(["📈 Γραφήματα", "⏱ Χρόνος Επίλυσης", "🗺️ Χάρτης", "📅 Χρονολόγιο"])

# --- TAB 1: Βασικά Γραφήματα Κατανομής ---
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        # Γράφημα Πίτας (Pie Chart) για την κατανομή των κατηγοριών
        fig1 = px.pie(df, names="category_name", title="Αναφορές ανά Κατηγορία")
        st.plotly_chart(fig1, width='stretch')
    with col2:
        # Ραβδόγραμμα (Bar Chart) για την κατανομή των καταστάσεων
        fig2 = px.bar(df["status_name"].value_counts().reset_index(),
                      x="status_name", y="count", color="status_name",
                      labels={"status_name": "Κατάσταση", "count": "Πλήθος"},
                      title="Αναφορές ανά Κατάσταση")
        st.plotly_chart(fig2, width='stretch')

    # Ιστόγραμμα (Histogram) ομαδοποιημένο ανά προτεραιότητα
    fig3 = px.histogram(df, x="category_name", color="priority", barmode="group",
                        labels={"category_name": "", "count": "Πλήθος"},
                        title="Προτεραιότητα ανά Κατηγορία")
    st.plotly_chart(fig3, width='stretch')


# --- TAB 2: Ανάλυση Χρόνου Επίλυσης ---
with tab2:
    st.subheader("⏱ Μέσος Χρόνος Επίλυσης ανά Κατηγορία")
    st.caption("Υπολογίζεται από τον πίνακα status_history — χρόνος από 'Αναφέρθηκε' έως 'Επιλύθηκε'")

    resolution_data = load_resolution_times()

    if not resolution_data:
        st.info("Δεν υπάρχουν ακόμα επιλυμένα προβλήματα στο ιστορικό.")
    else:
        res_df = pd.DataFrame(resolution_data)
        # Μετατροπή των στηλών σε αντικείμενα datetime
        res_df["resolved_at"] = pd.to_datetime(res_df["resolved_at"])
        res_df["created_at"]  = pd.to_datetime(res_df["created_at"])

        # Υπολογισμός χρόνου επίλυσης σε ώρες
        res_df["hours"] = (res_df["resolved_at"] - res_df["created_at"]).dt.total_seconds() / 3600

        # Μέσος χρόνος ανά κατηγορία
        avg_df = (
            res_df.groupby("category_name")["hours"]
            .mean()
            .round(1)
            .reset_index()
            .rename(columns={"hours": "Μέσες Ώρες", "category_name": "Κατηγορία"})
            .sort_values("Μέσες Ώρες", ascending=False)
        )

        col1, col2 = st.columns(2)

        with col1:
            # KPI — συνολικός μέσος χρόνος
            overall_avg = res_df["hours"].mean()
            st.metric(
                "⏱ Συνολικός Μέσος Χρόνος Επίλυσης",
                f"{overall_avg:.1f} ώρες",
                help="Μέσος χρόνος από την υποβολή έως την επίλυση"
            )
            st.metric(
                "✅ Συνολικά Επιλυμένα",
                len(res_df)
            )

        with col2:
            # Γράφημα Μέσου Χρόνου Επίλυσης με χρωματική κλίμακα (heatmap λογική)
            fig_res = px.bar(
                avg_df,
                x="Κατηγορία",
                y="Μέσες Ώρες",
                color="Μέσες Ώρες",
                color_continuous_scale="RdYlGn_r",
                title="Μέσος Χρόνος Επίλυσης ανά Κατηγορία (ώρες)",
                text="Μέσες Ώρες"
            )
            fig_res.update_traces(textposition="outside")
            fig_res.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig_res, width='stretch')

        # Αναλυτικός πίνακας δεδομένων
        st.subheader("Αναλυτικά")
        st.dataframe(avg_df, width='stretch', hide_index=True)

# --- TAB 3: Γεωχωρική Ανάλυση (Χάρτης) ---
with tab3:
    # Φιλτράρισμα προβλημάτων που έχουν έγκυρες συντεταγμένες
    map_df = df.dropna(subset=["latitude", "longitude"])
    if not map_df.empty:
        # Δημιουργία διαδραστικού χάρτη (Scatter Map)
        fig_map = px.scatter_map(map_df, lat="latitude", lon="longitude",
                                 color="category_name", hover_name="title",
                                 zoom=12, height=500, title="Θέσεις Αναφορών")
        fig_map.update_layout(map_style="open-street-map")
        st.plotly_chart(fig_map, width='stretch')

# --- TAB 4: Χρονοσειρές και Εξαγωγή Δεδομένων ---
with tab4:
    # Δημιουργία νέας στήλης μόνο με την ημερομηνία (χωρίς την ώρα)
    df["date"] = df["created_at"].dt.date
    # Καταμέτρηση αναφορών ανά ημέρα
    daily = df.groupby("date").size().reset_index(name="count")

    # Γράφημα Γραμμής (Line Chart) για την τάση των υποβολών
    fig4 = px.line(daily, x="date", y="count", markers=True,
                   title="Τάση Υποβολών",
                   labels={"date": "Ημερομηνία", "count": "Αριθμός Αναφορών"})
    st.plotly_chart(fig4, width='stretch')

    # Κουμπί εξαγωγής όλων των δεδομένων του συστήματος σε αρχείο CSV
    csv = df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button("⬇️ Κατέβασε CSV", csv, "cityreport.csv", "text/csv")
