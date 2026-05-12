import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="タコ・トレード", page_icon="🐙")
st.title("🐙 タコ・トレード分析室")

# --- APIキーの設定 (Google Gemini用) ---
api_key = st.secrets.get("OPENAI_API_KEY") or st.sidebar.text_input("Google API Key", type="password")

if st.button("タコ足分析を開始する"):
    if not api_key:
        st.error("APIキーが設定されていません。")
    else:
        # Google Geminiの設定
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        with st.spinner('タコの足が情報を収集しています...'):
            try:
                prompt = f"""
                あなたは優秀なトレーダー「タコ」です。
                銘柄コード【9759】について、以下の3つの視点からプロの分析を行ってください。

                1. 【ファンダメンタルの足】: 業績、配当、成長性について
                2. 【テクニカルの足】: 現在の株価水準、売り時・買い時の目安
                3. 【慎重・空売りの足】: 最悪のシナリオ（リスク要因）と損切りポイント

                最後に、中長期的な「総合評価」をタコらしくユーモアを交えて結論づけてください。
                """

                response = model.generate_content(prompt)
                
                st.markdown("---")
                st.subheader("📊 銘柄コード 9759 の分析結果")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
