import streamlit as st
import pandas as pd
from pathlib import Path

# -------------------- CONFIG --------------------
PASSWORDS = ["1234", "5678"]                 # tue password
CSV_PATH  = Path("dati.csv")
# -----------------------------------------------

# ---------- LOGIN ----------
def login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        with st.form("login"):
            pw = st.text_input("Password", type="password")
            ok = st.form_submit_button("Entra")
        if ok:
            if pw.strip() in PASSWORDS:
                st.session_state.logged_in = True
                st.experimental_rerun()
            else:
                st.error("Password errata")
        st.stop()
login()
# ---------- FINE LOGIN ----------

st.title("Gestione Attrezzature")

# Carica o crea DataFrame
if CSV_PATH.exists():
    df = pd.read_csv(CSV_PATH)
else:
    df = pd.DataFrame(columns=["Nome", "Cognome", "Telefono",
                               "Ufficio", "Attrezzature"])

# ---------- NUOVO INSERIMENTO ----------
with st.expander("➕ Aggiungi persona"):
    with st.form("add_form"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome")
            telefono = st.text_input("Telefono")
        with col2:
            cognome = st.text_input("Cognome")
            ufficio = st.text_input("Ufficio")
        attrezzature = st.text_area("Attrezzature (separate da virgole)")
        add_btn = st.form_submit_button("Aggiungi")

    if add_btn:
        nuova = {"Nome": nome,
                 "Cognome": cognome,
                 "Telefono": telefono,
                 "Ufficio": ufficio,
                 "Attrezzature": attrezzature}
        df = pd.concat([df, pd.DataFrame([nuova])], ignore_index=True)
        df.to_csv(CSV_PATH, index=False)
        st.success("Salvato!")

# ---------- RICERCA RAPIDA ----------
search = st.text_input("🔍 Cerca (Nome, Cognome, Ufficio)")
if search:
    mask = df.apply(lambda row: search.lower() in row.astype(str)
                    .str.lower().to_string(), axis=1)
    df_view = df[mask]
else:
    df_view = df

st.subheader(f"Elenco persone ({len(df_view)})")

# ---------- TABELLA EDITABILE ----------
edited_df = st.data_editor(
    df_view,
    num_rows="dynamic",
    key="editor",
)

# Se l’utente ha modificato qualcosa, aggiorna il DataFrame originale
if edited_df is not None and not edited_df.equals(df_view):
    # aggiorna solo le righe presenti in df_view
    df.update(edited_df)
    df.to_csv(CSV_PATH, index=False)
    st.success("Modifiche salvate!")

# ---------- ELIMINAZIONE ----------
with st.expander("🗑️ Cancella persona"):
    if len(df) == 0:
        st.info("Nessun record da cancellare")
    else:
        idx = st.selectbox(
            "Scegli la riga da cancellare",
            options=df.index,
            format_func=lambda i: f"{i} – {df.loc[i, 'Nome']} {df.loc[i, 'Cognome']}"
        )
        if st.button("Elimina definitivamente"):
            df.drop(idx, inplace=True)
            df.to_csv(CSV_PATH, index=False)
            st.success("Cancellato!")
            st.experimental_rerun()   # ricarica per puli_
