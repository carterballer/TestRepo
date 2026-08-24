import pandas as pd
import streamlit as st
from datetime import date as dt

######################################################################################################################################

# Daily Task Generation
def gen_daily(df, date):
    daily_tasks = df[df['frequency'] == 'daily'][['task','specified frequency']].copy()
    daily_tasks.columns = ['task','frequency']
    return daily_tasks

# Weekly Task Generation
def gen_weekly(df, date):
    day = date.strftime('%A').lower()
    weekly_tasks = df[df['specified frequency'] == day][['task','specified frequency']].copy()
    weekly_tasks.columns = ['task','frequency']
    return weekly_tasks

# Monthly Task Generation
def gen_monthly(df, date):
    day = date.strftime('%A').lower()
    monthly_tasks = df[
    (df['frequency'] == 'monthly') & (
        ((df['specified frequency'] == 'anyday') & (date.day in range(12,18)))
        | ((df['specified frequency'] == '25th') & (date.day == 25))
        | ((df['specified frequency'] == '2nd monday') & (day == 'monday') & (((date.day % 7) + 7) == date.day))
        | ((df['specified frequency'] == '1st saturday') & (day == 'saturday') & ((date.day % 7) == date.day))
    )][['task','specified frequency']].copy()
    monthly_tasks.columns = ['task','frequency']
    return monthly_tasks

# Otherly Task Generation
def gen_otherly(df, date):
    quarterly_tasks = df[(df['frequency'] == 'quarterly') & (date.month in [1,4,7,10])][['task','frequency']].copy()
    biyearly_tasks = df[(df['frequency'] == '6 months') & (date.month in [1,7])][['task','frequency']].copy()
    yearly_tasks = df[(df['frequency'] == 'yearly') & (date.month == 3)][['task','frequency']].copy()
    otherly_tasks = pd.concat([quarterly_tasks, biyearly_tasks, yearly_tasks], ignore_index = True)
    return otherly_tasks

# Generate All Tasks
def gen_all(df, date):
    total_tasks = pd.concat(
        [gen_daily(df, date), gen_weekly(df, date), gen_monthly(df, date), gen_otherly(df, date)],
        ignore_index=True)
    return total_tasks

######################################################################################################################################

# Load in Tasks
def load_data():
    df = pd.read_excel('tasks.xlsx')[['task','frequency','specified frequency']]
    df_comp = pd.read_excel('tasks_completion.xlsx')[['date','task','frequency','car completed','kam completed']]
    return df, df_comp

######################################################################################################################################

# Create new rows
def new_rows(df, date):
    total_tasks = gen_all(df, date)
    blank_row = pd.DataFrame({
        'date': date.strftime('%A, %Y-%m-%d'),
        'task': total_tasks['task'],
        'frequency': total_tasks['frequency'],
        'car completed': False,
        'kam completed': False})
    return blank_row

# Add new rows
def det_tasks(df, df_comp, date):
    date_str = date.strftime('%A, %Y-%m-%d')
    if date_str not in df_comp['date'].values:
        blank_row = new_rows(df, date)
        if date_str[-5:-3] not in df_comp['date'].values[-5:-3]:
            df_comp = pd.concat([blank_row, df_comp], ignore_index=True)
        else:
            blank_row = blank_row[blank_row['frequency'].isin(times+days)]
            df_temp = df_comp[
            (~df_comp['frequency'].isin(times+days))
            & ((df_comp['car completed'] == False)
            | (df_comp['kam completed'] == False))
            & (m1 == m2)]
            df_comp = pd.concat([blank_row, df_temp, df_comp], ignore_index=True)
    return df_comp

# Ask for completion
def completion(df_comp, date):
    if 'df_today' not in st.session_state:
        filtered_df = df_comp[df_comp['date'] == date.strftime('%A, %Y-%m-%d')].copy()
        filtered_df['car completed'] = filtered_df['car completed'].fillna(False).astype(bool)
        filtered_df['kam completed'] = filtered_df['kam completed'].fillna(False).astype(bool)
        st.session_state.df_today = filtered_df
    edited_df = st.data_editor(
        st.session_state.df_today,
        column_config = {
            'date': None,
            'task': st.column_config.TextColumn('task', disabled = True),
            'frequency': None,
            'car completed': st.column_config.CheckboxColumn('car done', help = 'car completion'),
            'kam completed': st.column_config.CheckboxColumn('kam done', help = 'choose')},
        hide_index = True,
        key = 'multi_checkbox_editor')
    if st.button('save', type = 'primary'):
        st.session_state.df_today = edited_df
        date_str = date.strftime('%A, %Y-%m-%d')
        mask = df_comp['date'] == date_str
        df_comp.loc[mask, ['car completed', 'kam completed']] = (
            st.session_state.df_today[['car completed', 'kam completed']].values
        )
        df_comp.to_excel('tasks_completion.xlsx', index=False)
        st.sidebar.success(f"Saved for {date_str}!")