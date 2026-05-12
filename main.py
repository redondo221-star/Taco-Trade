import streamlit as st
import google.generativeai as genai
import re

# ページ設定
st.set_page_config(page_title="株式投資戦略アシスタント", page_icon="📈")
st.title("📈 銘柄フォルダ連携・投資戦略システム")

# --- APIキーの設定 ---
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("Google API Keyを入力してください", type="password")

# --- 銘柄フォルダの貼り付けエリア ---
with st.expander("日経銘柄フォルダなどのリストを貼り付ける"):
    folder_text = st.text_area("ここにリストをペーストしてください", height=150, placeholder="例: 9759 NSD 2,844 ...")
    
    # 正規表現で4桁の数字（銘柄コード）を抽出
    found_codes = re.findall(r'\b\d{4}\b', folder_text)
    # 重複を削除してリスト化
    unique_codes = sorted(list(set(found_codes)))

# --- メイン画面 ---
if unique_codes:
    selected_code = st.selectbox("分析する銘柄を選択してください", unique_codes)
    user_input = selected_code
else:
    st.markdown("銘柄名またはコードを入力してください。")
    user_input = st.text_input("銘柄（コードまたは企業名）", value="9759")

# 最新の参考株価も入力できるように追加
current_price = st.text_input("現在の株価（任意・入力すると精度が上がります）", placeholder="例: 2844")

if st.button("投資戦略を生成する"):
    if not api_key:
        st.error("APIキーが設定されていません。")
    else:
        try:
            genai.configure(api_key=api_key)
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            target_model = next((m for m in available_models if 'flash' in m), available_models[0])
            model = genai.GenerativeModel(model_name=target_model)
            
            # 入力情報の整理
            context_input = f"{user_input} (現在値: {current_price}円)" if current_price else user_input
            
            with st.spinner(f"「{context_input}」の戦略を策定中..."):
                prompt = f"""
                あなたはプロの証券アナリストです。
                【{context_input}】について、以下の3つの時間軸で投資戦略を提示してください。
                提示された価格（もしあれば）を基準とし、最新の市場環境を考慮して具体的な「目安価格」を算出してください。

                ■ 1. 短期戦略（数日から数週間）
                ・テクニカル面からの買い時、利確、損切り価格の目安。
                
                ■ 2. 中期戦略（数ヶ月から1年）
                ・業績サイクルに基づいた目標株価。
                
                ■ 3. 長期戦略（数年以上）
                ・配当や事業成長性を踏まえた保有方針。

                回答は表形式や箇条書きを活用し、落ち着いた日本語でお願いします。
                ※実際の投資判断は自己責任である旨を最後に含めてください。
                """
                
                response = model.generate_content(prompt)
                st.session_state['strategy_result'] = response.text
                st.session_state['current_stock'] = user_input

        except Exception as e:
            st.error(f"エラーが発生しました: {str(e)}")

# 結果の表示（変更なし）
if 'strategy_result' in st.session_state:
    st.markdown("---")
    st.subheader(f"📊 {st.session_state['current_stock']} 投資戦略レポート")
    st.markdown(st.session_state['strategy_result'])
    
    st.markdown("#### さらに詳細を確認する")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("買いの根拠を詳しく聞く"):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(model_name='gemini-1.5-flash')
                res = model.generate_content(f"{st.session_state['current_stock']}の買いの妥当性について、指標を用いて解説してください。")
                st.info(res.text)
            except Exception as e: st.error(e)
    with col2:
        if st.button("下落時の対処法を聞く"):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(model_name='gemini-1.5-flash')
                res = model.generate_content(f"{st.session_state['current_stock']}の下落時の判断基準を教えてください。")
                st.warning(res.text)
            except Exception as e: st.error(e)
