import streamlit as st
import google.generativeai as genai

# ページ設定
st.set_page_config(page_title="株式投資戦略アシスタント", page_icon="📈")
st.title("📈 期間別 投資戦略システム")

# --- APIキーの設定 ---
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("Google API Keyを入力してください", type="password")

# --- メイン画面 ---
st.markdown("銘柄名またはコードを入力してください。期間別の戦略と目安株価を算出します。")
user_input = st.text_input("銘柄（コードまたは企業名）", value="9759")

if st.button("投資戦略を生成する"):
    if not api_key:
        st.error("APIキーが設定されていません。")
    else:
        try:
            genai.configure(api_key=api_key)
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            target_model = next((m for m in available_models if 'flash' in m), available_models[0])
            model = genai.GenerativeModel(model_name=target_model)
            
            with st.spinner(f"「{user_input}」の戦略を策定中..."):
                prompt = f"""
                あなたはプロの証券アナリスト兼ファンドマネージャーです。
                【{user_input}】について、以下の3つの時間軸で投資戦略を提示してください。
                現在の市場環境と直近の株価推移を推測し、具体的な「目安価格」を算出してください。

                ■ 1. 短期戦略（数日から数週間）
                ・テクニカル面からの買い時価格、利益確定（売り時）価格、損切り価格の目安。
                
                ■ 2. 中期戦略（数ヶ月から1年）
                ・業績サイクルやイベントに基づいた戦略。目標株価。
                
                ■ 3. 長期戦略（数年以上）
                ・配当や事業成長性を踏まえた保有方針。

                回答は表形式や箇条書きを活用し、簡潔かつ落ち着いた日本語でお願いします。
                ※注釈として「実際の投資判断は自己責任であること」を最後に含めてください。
                """
                
                response = model.generate_content(prompt)
                st.session_state['strategy_result'] = response.text
                st.session_state['current_stock'] = user_input

        except Exception as e:
            st.error(f"エラーが発生しました: {str(e)}")

# 結果の表示
if 'strategy_result' in st.session_state:
    st.markdown("---")
    st.subheader(f"📊 {st.session_state['current_stock']} 投資戦略レポート")
    st.markdown(st.session_state['strategy_result'])
    
    # --- 詳細質問ボタン ---
    st.markdown("#### さらに詳細を確認する")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("買いの根拠を詳しく聞く"):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(model_name='gemini-1.5-flash')
                res = model.generate_content(f"{st.session_state['current_stock']}について、なぜその買い時価格が妥当なのか、裏付けとなる指標（PERや移動平均線など）を詳しく解説してください。")
                st.info(res.text)
            except Exception as e:
                st.error(e)
            
    with col2:
        if st.button("下落時の対処法を聞く"):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(model_name='gemini-1.5-flash')
                res = model.generate_content(f"{st.session_state['current_stock']}の株価が想定外に下落した場合、どこでナンピンすべきか、あるいは完全に撤退すべきかの判断基準を教えてください。")
                st.warning(res.text)
            except Exception as e:
                st.error(e)
