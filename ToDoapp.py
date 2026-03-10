import streamlit as st
import pandas as pd
import os
from datetime import datetime, date

# 保存先のファイル名
DATA_FILE = "todo_calendar_list.csv"

# --- データの読み書き関数 ---
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        # 文字列として保存された日付を日付型に変換
        return df.to_dict(orient='records')
    return []

def save_data(todo_list):
    df = pd.DataFrame(todo_list)
    df.to_csv(DATA_FILE, index=False)

# アプリの初期化
if "todos" not in st.session_state:
    st.session_state.todos = load_data()

# ページ設定
st.set_page_config(page_title="Calendar ToDo", layout="wide")
st.title("カレンダー＆期限付きToDo管理")

# --- サイドバー：期限が近いタスク ---
st.sidebar.title("期限が近いタスク")
today = date.today()
for task in st.session_state.todos:
    # 文字列の日付を比較用に変換
    task_date = datetime.strptime(task['date'], '%Y-%m-%d').date()
    if not task['done'] and (task_date - today).days <= 3:
        st.sidebar.warning(f"あと{(task_date - today).days}日: {task['task']}")

# --- メイン画面：入力エリア ---
with st.expander("期限を決めてタスクを登録する", expanded=True):
    with st.form(key='todo_form', clear_on_submit=True):
        col_in1, col_in2, col_in3 = st.columns([2, 1, 1])
        with col_in1:
            new_task_name = st.text_input("タスク名", max_chars=50)
        with col_in2:
            # カレンダーから日付を選択
            task_date = st.date_input("期限", value=today)
        with col_in3:
            priority = st.selectbox("優先度", ["高", "中", "低"], index=1)
        
        submit_button = st.form_submit_button(label='追加')

    if submit_button and new_task_name:
        st.session_state.todos.append({
            "task": new_task_name, 
            "date": task_date.strftime('%Y-%m-%d'), # 文字列で保存
            "priority": priority, 
            "done": False
        })
        save_data(st.session_state.todos)
        st.rerun()

# --- メイン画面：タスク一覧 ---
st.write("### タスク一覧（期限順）")

# 期限が早い順に並び替え
sorted_todos = sorted(st.session_state.todos, key=lambda x: x['date'])

priority_colors = {"高": "red", "中": "orange", "低": "blue"}

for i, task in enumerate(sorted_todos):
    if not task['done']:
        p_color = priority_colors.get(task['priority'], "gray")
        c1, c2, c3, c4, c5 = st.columns([0.1, 0.5, 1, 2, 1])
        
        with c1:
            if st.checkbox("", key=f"chk_{i}"):
                task['done'] = True
                save_data(st.session_state.todos)
                st.rerun()
        with c2:
            st.markdown(f":{p_color}[[{task['priority']}]]")
        with c3:
            # 期限を表示
            st.write(f" {task['date']}")
        with c4:
            st.write(f"**{task['task']}**" if task['priority'] == "高" else task['task'])
        with c5:
            if st.button("削除", key=f"del_{i}"):
                st.session_state.todos.remove(task)
                save_data(st.session_state.todos)
                st.rerun()
                