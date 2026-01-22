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
    st.title("💼 Client Management System")

    # --- 2. DATA FETCHING ---
    df = get_clients()

    if not df.empty:
        # Cast types and clean headers
        df['client_num'] = pd.to_numeric(df['client_num'], errors='coerce')
        df['year_end'] = pd.Categorical(df['year_end'], categories=MONTHS, ordered=True)
        df.columns = [col.replace('_', ' ').upper() for col in df.columns]

        # --- 3. DASHBOARD & ANALYTICS ---
        st.subheader("📊 Practice Overview")
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("Total Clients", len(df))
        m_col2.metric("Active Portfolios", len(df[df['STATUS'] == 'Active']))
        m_col3.metric("Terminated", len(df[df['STATUS'] == 'Terminated']))

        st.write("### 📅 Monthly Year-End Distribution")
        # Prepare data for the chart
        month_counts = df['YEAR END'].value_counts().reindex(MONTHS).fillna(0)
        st.bar_chart(month_counts, color="#2E7D32")

        st.divider()

        # --- 4. MONTHLY PORTFOLIO VIEWER ---
        st.subheader("🔍 View by Month")
        selected_view_month = st.selectbox("Select Month to see upcoming audits:", MONTHS)
        
        monthly_filtered = df[df['YEAR END'] == selected_view_month]
        
        if not monthly_filtered.empty:
            st.success(f"Showing {len(monthly_filtered)} clients for {selected_view_month}")
            st.dataframe(monthly_filtered[['CLIENT NUM', 'NAME', 'UEN', 'STATUS']], 
                         use_container_width=True, hide_index=True)
        else:
            st.info(f"No clients have a Year-End in {selected_view_month}.")

        st.divider()

    # --- 5. SIDEBAR (ADD CLIENT) ---
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

    # --- 6. MAIN DATABASE & EDITING ---
    if not df.empty:
        st.subheader("📋 Master Client List")
        search_query = st.text_input("🔍 Search by Name or UEN", "")
        
        main_display_df = df.copy()
        if search_query:
            main_display_df = main_display_df[
                main_display_df['NAME'].str.contains(search_query, case=False, na=False) | 
                main_display_df['UEN'].str.contains(search_query, case=False, na=False)
            ]

        sort_col = st.selectbox("Sort Table by:", ["CLIENT NUM", "YEAR END", "NAME"])
        st.dataframe(main_display_df.sort_values(by=sort_col), use_container_width=True, hide_index=True)

        # --- 7. EDIT / DELETE ---
        st.subheader("📝 Modification Panel")
        client_options = {f"{row['NAME']} (ID: {row['ID']})": row['ID'] for _, row in main_display_df.iterrows()}
        
        if client_options:
            selected_option = st.selectbox("Pick a client to edit:", list(client_options.keys()))
            selected_id = client_options[selected_option]
            client_info = df[df['ID'] == selected_id].iloc[0]
            
            with st.expander(f"Update Details for {client_info['NAME']}"):
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    e_num = st.number_input("Edit Num", value=int(client_info['CLIENT NUM']))
                    e_name = st.text_input("Edit Name", value=str(client_info['NAME']))
                    e_uen = st.text_input("Edit UEN", value=str(client_info['UEN']))
                with col_e2:
                    curr_m = str(client_info['YEAR END'])
                    m_idx = MONTHS.index(curr_m) if curr_m in MONTHS else 0
                    e_month = st.selectbox("Edit Year End", MONTHS, index=m_idx)
                    e_status = st.selectbox("Edit Status", ["Active", "Terminated"], 
                                           index=0 if client_info['STATUS'] == "Active" else 1)

                b1, b2, _ = st.columns([1, 1, 2])
                if b1.button("✅ Save Changes", type="primary"):
                    update_client(selected_id, e_num, e_name, e_uen, e_month, e_status)
                    st.rerun()
                if b2.button("🗑️ Delete"):
                    delete_client(selected_id)
                    st.rerun()