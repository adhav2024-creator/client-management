import streamlit as st
import pandas as pd
from database import init_db, get_clients, add_client, delete_client, update_client

# --- 1. CONFIGURATION & LOGIN ---
st.set_page_config(page_title="Audit Client Tracker", layout="wide")
init_db()

# Constants
MONTHS = ["January", "February", "March", "April", "May", "June", 
          "July", "August", "September", "October", "November", "December"]

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]:
        return True

    st.title("🔒 Audit Firm Secure Login")
    password = st.text_input("Enter Office Password", type="password")
    if st.button("Login"):
        if password == "Awesome2050@": 
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("Wrong password.")
    return False

# --- 2. THE APP CONTENT ---
if check_password():
    st.title("📂 Client Management System")

    # --- Sidebar: Add New Client ---
    st.sidebar.header("Add New Client")
    with st.sidebar.form("add_form", clear_on_submit=True):
        new_num = st.text_input("Client Number")
        new_name = st.text_input("Name of Customer")
        new_uen = st.text_input("UEN Number")
        new_month = st.selectbox("Year End Month", MONTHS)
        new_status = st.selectbox("Status", ["Active", "Terminated"])
        
        if st.form_submit_button("Save New Client"):
            if new_num and new_name:
                add_client(new_num, new_name, new_uen, new_month, new_status)
                st.success("Client Added!")
                st.rerun()
            else:
                st.error("Client Number and Name are required.")

    # --- Main Screen: View, Sort & Edit ---
    df = get_clients()

    if not df.empty:
        # Sorting
        sort_col = st.selectbox("Sort data by:", ["client_num", "year_end", "name"])
        df = df.sort_values(by=sort_col)

        st.subheader("Client Database")
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.divider()

        # --- Edit / Delete Section ---
        st.subheader("📝 Edit or Delete Client Details")
        
        # Select client to modify
        client_names = df['name'].tolist()
        selected_client_name = st.selectbox("Select a client to modify:", client_names)
        
        # Get the current data for the selected client
        client_info = df[df['name'] == selected_client_name].iloc[0]
        
        # Layout for Editing
        with st.expander(f"Modify Details for {selected_client_name}", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                edit_num = st.text_input("Client Number", value=client_info['client_num'])
                edit_name = st.text_input("Customer Name", value=client_info['name'])
                edit_uen = st.text_input("UEN", value=client_info['uen'])
            
            with col2:
                # Find index of current month for the dropdown
                month_idx = MONTHS.index(client_info['year_end']) if client_info['year_end'] in MONTHS else 0
                edit_month = st.selectbox("Year End", MONTHS, index=month_idx)
                
                status_idx = 0 if client_info['status'] == "Active" else 1
                edit_status = st.selectbox("Client Status", ["Active", "Terminated"], index=status_idx)

            # Buttons
            btn_col1, btn_col2, _ = st.columns([1, 1, 2])
            
            if btn_col1.button("💾 Update Details", type="primary"):
                update_client(client_info['id'], edit_num, edit_name, edit_uen, edit_month, edit_status)
                st.success("Client updated!")
                st.rerun()
                
            if btn_col2.button("🗑️ Delete Client"):
                delete_client(client_info['id'])
                st.warning("Client deleted.")
                st.rerun()
    else:
        st.info("No clients found. Use the sidebar to add your first client.")