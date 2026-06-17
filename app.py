import streamlit as st
import pandas as pd
from datetime import datetime
import os

FILE = "tasks.csv"


# ---------------------------
# 初期化
# ---------------------------
def init_state():
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        st.session_state.bu = ""
        st.session_state.requester = ""
        st.session_state.task = ""
        st.session_state.status = ""
        st.session_state.deadline = None
        st.session_state.assignee = ""


init_state()


# ---------------------------
# データ処理（CSV版）
# ---------------------------
def load_data():
    if os.path.exists(FILE):
        return pd.read_csv(FILE)
    else:
        df = pd.DataFrame(columns=[
            "部署",
            "依頼者",
            "タスク内容",
            "状態",
            "期限",
            "対応者",
            "開始日",
            "アップデート日"
        ])
        df.to_csv(FILE, index=False)
        return df


def save_data(df):
    df.to_csv(FILE, index=False)


def add_task(bu, requester, task, status, deadline, assignee):
    df = load_data()

    new_task = {
        "部署": bu,
        "依頼者": requester,
        "タスク内容": task,
        "状態": status,
        "期限": str(deadline),
        "対応者": assignee,
        "開始日": datetime.now().strftime("%Y-%m-%d"),
        "アップデート日": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    df = pd.concat([df, pd.DataFrame([new_task])], ignore_index=True)
    save_data(df)


def update_status(index, status):
    df = load_data()
    df.loc[index, "状態"] = status
    df.loc[index, "アップデート日"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_data(df)


def delete_completed():
    df = load_data()
    df = df[df["状態"] != "完了"].reset_index(drop=True)
    save_data(df)


# ---------------------------
# UI
# ---------------------------
st.title("タスク管理システム")

# ---------------------------
# タスク追加
# ---------------------------
st.header("タスク追加")

bu = st.selectbox("タスク名", ["", "建技", "トラ技", "その他"], key="bu")
requester = st.text_input("依頼者", key="requester")
task = st.text_input("タスク内容", key="task")
status_input = st.selectbox("状態", ["", "未着手", "進行中", "完了"], key="status")
deadline = st.date_input("期限", key="deadline")
assignee = st.selectbox("対応者", ["", "山中", "池原", "栂野"], key="assignee")

if st.button("追加"):
    add_task(bu, requester, task, status_input, deadline, assignee)
    st.success("追加しました")
    st.session_state.clear()
    st.rerun()


# ---------------------------
# リセット
# ---------------------------
if st.button("リセット"):
    st.session_state.clear()
    st.rerun()


# ---------------------------
# 一覧
# ---------------------------
st.header("タスク一覧")
df = load_data()
st.dataframe(df)


# ---------------------------
# 状態更新
# ---------------------------
st.header("状態更新")

df = load_data()

if len(df) > 0:
    idx = st.selectbox("行選択", df.index)
    status_update = st.selectbox(
        "状態",
        ["未着手", "進行中", "完了"],
        key="status_select"
    )

    if st.button("更新"):
        update_status(idx, status_update)
        st.success("更新しました")


# ---------------------------
# 完了済み一括削除
# ---------------------------
st.header("一括削除（完了済み）")

if st.button("完了済みを全削除"):
    delete_completed()
    st.success("完了済みを削除しました")
    st.rerun()


# ---------------------------
# 複数削除（番号）
# ---------------------------
st.header("個別削除（複数番号）")

df = load_data()

if len(df) > 0:
    display_df = df.copy()
    display_df.insert(0, "No", display_df.index)

    st.dataframe(display_df)

    delete_indexes = st.multiselect(
        "削除するNo",
        options=df.index
    )

    if st.button("選択したタスクを削除"):
        if delete_indexes:
            df = df.drop(delete_indexes).reset_index(drop=True)
            save_data(df)
            st.success(f"{delete_indexes} を削除しました")
            st.rerun()
        else:
            st.warning("削除対象が選択されていません")