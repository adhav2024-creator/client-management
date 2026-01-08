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
    st.title(" Client Management System")

    df = get_clients()

  
    if not df.empty:
        st.subheader("📊 Practice Overview")
        
        
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("Total Clients", len(df))
        m_col2.metric("Active Portfolios", len(df[df['status'] == 'Active']))
        m_col3.metric("Terminated", len(df[df['status'] == 'Terminated']))

       
        st.write("###  Client Load by Month")
        month_counts = df['year_end'].value_counts()
        summary_data = pd.DataFrame({
            'Month': MONTHS,
            'Count': [month_counts.get(m, 0) for m in MONTHS]
        })
        
        
        st.dataframe(summary_data.set_index('Month').T, use_container_width=True)
        st.divider()

    
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
                st.error("Fields required.")

   
    if not df.empty:
        st.subheader("📋 Client Database")
        
       
        search_query = st.text_input("🔍 Search by Client Name or UEN", "")
        
        # Filter dataframe based on search
        if search_query:
            df = df[
                df['name'].str.contains(search_query, case=False, na=False) | 
                df['uen'].str.contains(search_query, case=False, na=False)
            ]

        # Sorting
        sort_col = st.selectbox("Sort data by:", ["client_num", "year_end", "name"])
        df_sorted = df.sort_values(by=sort_col)
        
        st.dataframe(df_sorted, use_container_width=True, hide_index=True)

        st.divider()

        # --- Edit / Delete Section ---
        st.subheader("📝 Edit or Delete Client Details")
        
        if not df.empty:
            client_options = {f"{row['name']} (ID: {row['id']})": row['id'] for _, row in df.iterrows()}
            selected_option = st.selectbox("Select a client to modify:", list(client_options.keys()))
            selected_id = client_options[selected_option]
            
            client_info = df[df['id'] == selected_id].iloc[0]
            
            with st.expander(f"Modify Details for {client_info['name']}", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    edit_num = st.text_input("Client Number", value=str(client_info['client_num']))
                    edit_name = st.text_input("Customer Name", value=str(client_info['name']))
                    edit_uen = st.text_input("UEN", value=str(client_info['uen']))
                with col2:
                    current_month = str(client_info['year_end'])
                    month_idx = MONTHS.index(current_month) if current_month in MONTHS else 0
                    edit_month = st.selectbox("Year End", MONTHS, index=month_idx)
                    
                    status_list = ["Active", "Terminated"]
                    current_status = str(client_info['status'])
                    status_idx = status_list.index(current_status) if current_status in status_list else 0
                    edit_status = st.selectbox("Client Status", status_list, index=status_idx)

                btn_col1, btn_col2, _ = st.columns([1, 1, 2])
                if btn_col1.button("✅ Update Details", type="primary"):
                    update_client(int(client_info['id']), edit_num, edit_name, edit_uen, edit_month, edit_status)
                    st.success("Updated!")
                    st.rerun()
                    
                if btn_col2.button("🗑️ Delete Client"):
                    delete_client(int(client_info['id']))
                    st.warning("Deleted.")
                    st.rerun()
        else:
            st.info("No clients match your search.")
    else:
        st.info("No clients found.")