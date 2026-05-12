import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="タコ・トレード", page_icon="🐙")
st.title("🐙 タコ・トレード分析室")

# --- 設定（サイドバー） ---
st.sidebar.header("設定")
# Secretsの名前が間違っていても動くように、複数の候補を確認するようにしました
api_key = (st.secrets.get("GEMINI_API_KEY") or 
           st.secrets.get("OPENAI_API_KEY") or 
           st.sidebar.text_input("Google API Key", type="password"))

# --- メイン画面 ---
stock_code = st.text_input("分析したい銘柄コードを入力（例: 9759）", value="9759")

if st.button("タコ足分析を開始する"):
    if not api_key:
        st.error("APIキーを入力してください。左のサイドバー、またはSecrets設定が必要です。")
    else:
        try:
            # Google Geminiの初期化
            genai.configure(api_key=api_key)
            
            # モデルを 'gemini-1.5-flash' に固定（これが一番速くて安定しています）
            model = genai.GenerativeModel('gemini-pro')
            
            with st.spinner(f'銘柄 {stock_code} をタコ足分析中... 8本の足で調査しています。'):
                # AIへの命令
                prompt = f"""
                あなたは凄腕の株式投資トレーダー「タコ」です。
                銘柄コード【{stock_code}】について、以下の3つの視点からプロの分析を行ってください。

                1. 【ファンダメンタルの足】: 業績、配当、成長性について
                2. 【テクニカルの足】: 現在の株価水準、売り時・買い時の目安
                3. 【慎重・空売りの足】: リスク要因と損切りポイント

                最後に、中長期的な「総合評価」をタコらしくユーモア（「〜だタコ」など）を交えて結論づけてください。
                回答は必ず日本語でお願いします。
                """

                # タイムアウト対策として、少し簡潔な回答を求める設定
                response = model.generate_content(prompt)
                
                if response.text:
                    st.markdown("---")
                    st.subheader(f"📊 銘柄コード {stock_code} の分析結果")
                    st.markdown(response.text)
                else:
                    st.warning("AIからの返答が空でした。もう一度試してみてください。")
                
        except Exception as e:
            # 何が原因で止まっているか、詳細を表示します
            st.error(f"タコの足がもつれました（エラー）: {str(e)}")
            st.info("APIキーが正しいか、または有効期限が切れていないか確認してください。")
