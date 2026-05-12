import streamlit as st

st.set_page_config(page_title="タコ・トレード", page_icon="🐙")
st.title("🐙 タコ・トレード分析室")

st.sidebar.header("設定")
api_key = st.sidebar.text_input("OpenAI API Key", type="password")

stock_code = st.text_input("銘柄コードを入力してください（例: 9759）", value="9759")

if st.button("タコ足分析を開始する"):
    if not api_key:
        st.error("APIキーを入力してください。")
    else:
        st.write(f"現在、{stock_code} を『ファンダメンタル・テクニカル・慎重』の3視点で分析する準備をしています...")
        # ここに後ほどAIのロジックを組み込みます
