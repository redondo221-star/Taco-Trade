import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="タコ・トレード", page_icon="🐙")
st.title("🐙 タコ・トレード分析室")

# --- 設定（サイドバー） ---
st.sidebar.header("設定")
api_key = (st.secrets.get("GEMINI_API_KEY") or 
           st.sidebar.text_input("Google API Key", type="password"))

# --- メイン画面 ---
stock_code = st.text_input("分析したい銘柄コードを入力（例: 9759）", value="9759")

if st.button("タコ足分析を開始する"):
    if not api_key:
        st.error("APIキーを入力してください。")
    else:
        try:
            # 最新のAPI設定
            genai.configure(api_key=api_key)
            
            # 【重要】2026年現在、最も推奨されるモデル名に修正
            # エラーが出にくい 'gemini-1.5-flash' を使用します
            model = genai.GenerativeModel(model_name='gemini-1.5-flash')
            
            with st.spinner(f'銘柄 {stock_code} をタコ足分析中...'):
                prompt = f"""
                あなたは凄腕トレーダー「タコ」です。
                銘柄コード【{stock_code}】について、以下の3点からプロの分析を行ってください。
                1. 【ファンダメンタル】業績・配当
                2. 【テクニカル】売り時・買い時
                3. 【慎重派の視点】リスク要因
                結論はタコらしくユーモア（語尾に「〜だタコ」など）を交えて日本語で回答してください。
                """
                
                # 世代生成の実行
                response = model.generate_content(prompt)
                
                if response:
                    st.markdown("---")
                    st.subheader(f"📊 {stock_code} の分析結果")
                    st.write(response.text)
                
        except Exception as e:
            # まだエラーが出る場合は、モデル名の指定を 'models/gemini-1.5-flash' に自動切り替え
            try:
                model = genai.GenerativeModel(model_name='models/gemini-1.5-flash')
                response = model.generate_content(prompt)
                st.write(response.text)
            except:
                st.error(f"タコの足がもつれました: {str(e)}")
                st.info("APIキーの権限、またはモデル名の指定に問題がある可能性があります。")
