from datetime import date as dt
import streamlit as st
import pandas as pd
from tasks import *

st.set_page_config(page_title='Daily Hub')
st.title('baller tasks')

def on_date_change():
    if 'df_today' in st.session_state:
        del st.session_state['df_today']
with st.sidebar:
    st.header('controls')
    
    if 'date' not in st.session_state:
        st.session_state.date = dt.today()
        
    st.date_input(
        'select date',
        key = 'date',
        on_change = on_date_change
    )
    st.divider()

# Load data
df, df_comp = load_data()

if df_comp.empty:
    df_comp = new_rows(df, st.session_state.date).copy()
else:
    df_comp = det_tasks(df, df_comp, st.session_state.date)
    
completion(df_comp, st.session_state.date)