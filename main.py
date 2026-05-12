import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="タコ・トレード", page_icon="🐙")
st.title("🐙 タコ・トレード分析室")

# --- 設定（サイドバー） ---
st.sidebar.header("設定")
# Secretsになければ手動入力を促す
api_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("Google API Key", type="password")

# --- メイン画面：入力欄 ---
# ボタンの外に出しておくことで、分析中も消えなくなります
stock_code = st.text_input("分析したい銘柄コードを入力（例: 9759）", value="9759")

if st.button("タコ足分析を開始する"):
    if not api_key:
        st.error("APIキーを入力してください。")
    else:
        # Google Geminiの設定
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # ローディング表示
        with st.spinner(f'銘柄 {stock_code} をタコ足分析中... しばらくお待ちください。'):
            try:
                prompt = f"""
                あなたは優秀な投資家トレーダー「タコ」です。
                銘柄コード【{stock_code}】について、以下の3つの視点からプロの分析を行ってください。

                1. 【ファンダメンタルの足】: 業績、配当、成長性について
                2. 【テクニカルの足】: 現在の株価水準、売り時・買い時の目安
                3. 【慎重・空売りの足】: 最悪のシナリオ（リスク要因）と損切りポイント

                最後に、中長期的な「総合評価」をタコらしくユーモアを交えて結論づけてください。
                回答は日本語でお願いします。
                """

                response = model.generate_content(prompt)
                
                # 結果を表示
                st.markdown("---")
                st.subheader(f"📊 銘柄コード {stock_code} の分析結果")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
