import streamlit as st
import google.generativeai as genai

# ページ設定
st.set_page_config(page_title="株式投資分析アシスタント", page_icon="📈")
st.title("📈 株式投資分析システム")

# --- APIキーの設定 ---
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("Google API Keyを入力してください", type="password")

# --- メイン画面 ---
st.markdown("銘柄コードまたは企業名を入力してください。ポイントを絞って要約分析します。")
user_input = st.text_input("銘柄コード または 企業名", value="9759")

if st.button("要約分析を実行する"):
    if not api_key:
        st.error("APIキーが設定されていません。")
    else:
        try:
            genai.configure(api_key=api_key)
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            target_model = next((m for m in available_models if 'flash' in m), available_models[0])
            model = genai.GenerativeModel(model_name=target_model)
            
            with st.spinner(f"「{user_input}」を分析中..."):
                prompt = f"""
                あなたはプロの証券アナリストです。
                入力された【{user_input}】について、投資判断に必要なポイントを極力短く、箇条書きでまとめてください。
                
                ■ 構成
                1. 正式な企業名と銘柄コード
                2. 【業績のポイント】（2-3点）
                3. 【株価・チャートの印象】（1-2点）
                4. 【最大のリスク要因】（1点）
                
                余計な解説は省き、事実と専門的な見解のみを簡潔に述べてください。
                回答は落ち着いた丁寧な日本語でお願いします。
                """
                
                response = model.generate_content(prompt)
                st.session_state['analysis_result'] = response.text
                st.session_state['last_input'] = user_input

        except Exception as e:
            st.error(f"エラーが発生しました: {str(e)}")

# 結果の表示
if 'analysis_result' in st.session_state:
    st.markdown("---")
    st.subheader(f"📊 {st.session_state['last_input']} の要約レポート")
    st.write(st.session_state['analysis_result'])
    
    # --- 深掘りボタン ---
    if st.button("この銘柄についてさらに詳しく聞く"):
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name='gemini-1.5-flash')
            with st.spinner("詳細データを収集中..."):
                detail_prompt = f"先ほどの要約内容を踏まえ、【{st.session_state['last_input']}】について、今後の成長戦略や具体的な目標株価の考え方、競合他社との比較など、より踏み込んだ詳細な分析を提供してください。"
                detail_response = model.generate_content(detail_prompt)
                st.markdown("### 🔍 詳細分析結果")
                st.write(detail_response.text)
        except Exception as e:
            st.error(f"詳細分析中にエラーが発生しました: {str(e)}")
