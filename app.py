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
        # Matches your provided password
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
        # Displaying 'id' is helpful for debugging, but you can hide it in hide_index
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.divider()

        # --- Edit / Delete Section ---
        st.subheader("📝 Edit or Delete Client Details")
        
        # Select client to modify - Using Name + ID to ensure uniqueness
        client_options = {f"{row['name']} (ID: {row['id']})": row['id'] for _, row in df.iterrows()}
        selected_option = st.selectbox("Select a client to modify:", list(client_options.keys()))
        selected_id = client_options[selected_option]
        
        # Pull the specific record data using the selected ID
        client_info = df[df['id'] == selected_id].iloc[0]
        
        # Layout for Editing
        with st.expander(f"Modify Details for {client_info['name']}", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                edit_num = st.text_input("Client Number", value=str(client_info['client_num']))
                edit_name = st.text_input("Customer Name", value=str(client_info['name']))
                edit_uen = st.text_input("UEN", value=str(client_info['uen']))
            
            with col2:
                # Find index of current month for the dropdown
                current_month = str(client_info['year_end'])
                month_idx = MONTHS.index(current_month) if current_month in MONTHS else 0
                edit_month = st.selectbox("Year End", MONTHS, index=month_idx)
                
                status_list = ["Active", "Terminated"]
                current_status = str(client_info['status'])
                status_idx = status_list.index(current_status) if current_status in status_list else 0
                edit_status = st.selectbox("Client Status", status_list, index=status_idx)

            # Buttons
            btn_col1, btn_col2, _ = st.columns([1, 1, 2])
            
            # Using the ID as an integer for the database calls
            target_id = int(client_info['id'])

            if btn_col1.button("✅ Update Details", type="primary", key="update_btn"):
                update_client(target_id, edit_num, edit_name, edit_uen, edit_month, edit_status)
                st.success("Client updated successfully!")
                st.rerun()
                
            if btn_col2.button("🗑️ Delete Client", key="delete_btn"):
                delete_client(target_id)
                st.warning("Client record removed.")
                st.rerun()
    else:
        st.info("No clients found. Use the sidebar to add your first client.")