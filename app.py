import streamlit as st
import pandas as pd
from database import init_db, get_clients, add_client, delete_client

# --- 1. CONFIGURATION & LOGIN ---
st.set_page_config(page_title="Audit Client Tracker", layout="wide")
init_db()

def check_password():
    """Returns True if the user had the correct password."""
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    # Show input for password
    st.title("🔒 Audit Firm Secure Login")
    password = st.text_input("Enter Office Password", type="password")
    if st.button("Login"):
        if password == "Audit2024!":  # CHANGE YOUR PASSWORD HERE
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("Wrong password. Please try again.")
    return False

# --- 2. THE APP CONTENT ---
if check_password():
    st.title("📂 Client Management System")

    # --- Sidebar: Add Client ---
    st.sidebar.header("Add New Client")
    with st.sidebar.form("add_form", clear_on_submit=True):
        new_num = st.text_input("Client Number")
        new_name = st.text_input("Name of Customer")
        new_uen = st.text_input("UEN Number")
        new_ye = st.date_input("Year End")
        new_status = st.selectbox("Status", ["Active", "Terminated"])
        submit = st.form_submit_button("Save Client")

        if submit:
            if new_num and new_name:
                add_client(new_num, new_name, new_uen, str(new_ye), new_status)
                st.success("Added!")
                st.rerun()
            else:
                st.error("Please fill required fields.")

    # --- Main Screen: View & Sort ---
    df = get_clients()

    if not df.empty:
        # Sorting Options
        sort_col = st.selectbox("Sort data by:", ["client_num", "year_end", "name"])
        df = df.sort_values(by=sort_col)

        # Display Table
        st.subheader("Client Database")
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Delete Section
        st.divider()
        st.subheader("Delete Record")
        id_to_del = st.selectbox("Select ID to remove", df['id'].tolist())
        if st.button("Confirm Delete"):
            delete_client(id_to_del)
            st.warning(f"Record {id_to_del} deleted.")
            st.rerun()
    else:
        st.info("No clients found. Use the sidebar to add your first client.")