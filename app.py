import streamlit as st
import pandas as pd
from database import init_db, get_clients, add_client, delete_client, update_client

# --- 1. CONFIGURATION & LOGIN ---
st.set_page_config(page_title="Audit Client Tracker", layout="wide")
init_db()

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

if check_password():
    st.title("Client Management System")

    # --- 2. DATA FETCHING & TYPE CASTING ---
    df = get_clients()

    if not df.empty:
        # 1. Ensure numeric sorting for client_num
        df['client_num'] = pd.to_numeric(df['client_num'], errors='coerce')
        
        # 2. Set months as categorical for calendar sorting
        df['year_end'] = pd.Categorical(df['year_end'], categories=MONTHS, ordered=True)

        # 3. CAPITALIZE HEADERS
        # This replaces underscores with spaces and capitalizes every word
        df.columns = [col.replace('_', ' ').upper() for col in df.columns]

        st.subheader("📊 Practice Overview")
        # Note: Metrics and logic below use capitalized names now
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("Total Clients", len(df))
        m_col2.metric("Active Portfolios", len(df[df['STATUS'] == 'Active']))
        m_col3.metric("Terminated", len(df[df['STATUS'] == 'Terminated']))

        st.divider()

    # --- 3. SIDEBAR (ADD CLIENT) ---
    st.sidebar.header("Add New Client")
    with st.sidebar.form("add_form", clear_on_submit=True):
        new_num = st.number_input("Client Number", min_value=1, step=1)
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
                st.error("Fields required.")

    # --- 4. MAIN DISPLAY & SEARCH ---
    if not df.empty:
        st.subheader("📋 Client Database")
        search_query = st.text_input("🔍 Search by Client Name or UEN", "")
        
        filtered_df = df.copy()
        if search_query:
            # Search logic updated for capitalized headers
            filtered_df = filtered_df[
                filtered_df['NAME'].str.contains(search_query, case=False, na=False) | 
                filtered_df['UEN'].str.contains(search_query, case=False, na=False)
            ]

        # Sorting Logic - using capitalized names
        sort_col = st.selectbox("Sort data by:", ["CLIENT NUM", "YEAR END", "NAME"])
        df_sorted = filtered_df.sort_values(by=sort_col)
        
        st.dataframe(df_sorted, use_container_width=True, hide_index=True)
        st.divider()

        # --- 5. EDIT / DELETE SECTION ---
        st.subheader("📝 Edit or Delete Client Details")
        
        # Mapping updated for capitalized headers
        client_options = {f"{row['NAME']} (ID: {row['ID']})": row['ID'] for _, row in filtered_df.iterrows()}
        if client_options:
            selected_option = st.selectbox("Select a client to modify:", list(client_options.keys()))
            selected_id = client_options[selected_option]
            client_info = df[df['ID'] == selected_id].iloc[0]
            
            with st.expander(f"Modify Details for {client_info['NAME']}", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    edit_num = st.number_input("Client Number", value=int(client_info['CLIENT NUM']))
                    edit_name = st.text_input("Customer Name", value=str(client_info['NAME']))
                    edit_uen = st.text_input("UEN", value=str(client_info['UEN']))
                with col2:
                    current_month = str(client_info['YEAR END'])
                    month_idx = MONTHS.index(current_month) if current_month in MONTHS else 0
                    edit_month = st.selectbox("Year End", MONTHS, index=month_idx)
                    
                    status_list = ["Active", "Terminated"]
                    current_status = str(client_info['STATUS'])
                    status_idx = status_list.index(current_status) if current_status in status_list else 0
                    edit_status = st.selectbox("Client Status", status_list, index=status_idx)

                btn_col1, btn_col2, _ = st.columns([1, 1, 2])
                if btn_col1.button("✅ Update Details", type="primary"):
                    # Use original ID to update
                    update_client(int(client_info['ID']), edit_num, edit_name, edit_uen, edit_month, edit_status)
                    st.success("Updated!")
                    st.rerun()
                    
                if btn_col2.button("🗑️ Delete Client"):
                    delete_client(int(client_info['ID']))
                    st.warning("Deleted.")
                    st.rerun()
        else:
            st.info("No clients match your search.")
    else:
        st.info("No clients found.")