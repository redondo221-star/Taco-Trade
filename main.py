import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="タコ・トレード", page_icon="🐙")
st.title("🐙 タコ・トレード分析室")

# --- 設定（サイドバー） ---
st.sidebar.header("設定")
api_key = (st.secrets.get("GEMINI_API_KEY") or 
           st.secrets.get("OPENAI_API_KEY") or 
           st.sidebar.text_input("Google API Key", type="password"))

# --- メメイン画面 ---
stock_code = st.text_input("分析したい銘柄コードを入力（例: 9759）", value="9759")

if st.button("タコ足分析を開始する"):
    if not api_key:
        st.error("APIキーを入力してください。")
    else:
        try:
            genai.configure(api_key=api_key)
            
            # モデル名を 'gemini-pro' に変更して安定性を高めます
            model = genai.GenerativeModel('gemini-pro')
            
            with st.spinner(f'銘柄 {stock_code} を調査中...'):
                prompt = f"""
                あなたは凄腕トレーダー「タコ」です。
                銘柄コード【{stock_code}】について、以下の3点からプロの分析を行ってください。
                1. 【ファンダメンタル】業績・配当
                2. 【テクニカル】売り時・買い時
                3. 【慎重派の視点】リスク要因
                結論はタコらしくユーモアを交えて日本語で回答してください。
                """
                
                response = model.generate_content(prompt)
                
                st.markdown("---")
                st.subheader(f"📊 {stock_code} の分析結果")
                st.write(response.text)
                
        except Exception as e:
            st.error(f"タコの足がもつれました（エラー）: {str(e)}")
