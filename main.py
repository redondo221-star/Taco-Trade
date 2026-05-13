import streamlit as st
import google.generativeai as genai
import re
import time

# ページ設定
st.set_page_config(page_title="Tacoトレード", page_icon="🐙")
st.title("🐙 Tacoトレード")

# --- APIキーの設定 ---
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("Google API Keyを入力してください", type="password")

# --- サイドバー設定 ---
st.sidebar.header("分析設定")
risk_level = st.sidebar.slider("リスク許容度", 1, 5, 3, help="1:慎重 ～ 5:積極的")
investment_style = st.sidebar.multiselect("スタイル", ["短期", "中期", "長期"], default=["中期"])

# 【修正版】最新の安定モデルを指定
def get_model(api_key):
    genai.configure(api_key=api_key)
    # 2026年現在、最も無料枠が広く安定しているモデルを指定します
    # 1.5-flashがエラーになる場合は、こちらを試してください
    try:
        return genai.GenerativeModel(model_name="gemini-2.5-flash")
    except:
        # 万が一上記が利用不可な場合、利用可能な最新のFlashを探す
        return genai.GenerativeModel(model_name="gemini-1.5-flash-latest")

# --- 分析実行用ヘルパー ---
def safe_generate(model, prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "ResourceExhausted" in error_msg:
            return "⚠️【回数制限】Googleの無料枠を使い切りました。1分待つか、別プロジェクトのAPIキーをお試しください。"
        return f"⚠️ エラーが発生しました: {error_msg}"

# --- 1. 銘柄フォルダの読み込み ---
st.markdown("### 1. 銘柄フォルダの読み込み")
folder_text = st.text_area("日経銘柄フォルダ情報を貼り付け", height=100, key="folder_input")

col1, col2 = st.columns(2)
with col1:
    if st.button("全銘柄をスキャン"):
        if folder_text and api_key:
            with st.spinner("スキャン中..."):
                model = get_model(api_key)
                # スキャン時の負荷を下げるため、より簡潔なプロンプトに変更
                prompt = f"以下の銘柄リストから買い・売りの注目株を各2〜3銘柄ずつ、理由と共に超簡潔に抽出して。リスト:\n{folder_text}"
                st.session_state['screen_result'] = safe_generate(model, prompt)
                # 銘柄名抽出
                matches = re.findall(r'(\d{4})\s+[^\s\d]+\s+([^\s\d]+)', folder_text)
                st.session_state['display_list'] = [f"{m[0]} {m[1]}" for m in matches] if matches else re.findall(r'\b\d{4}\b', folder_text)

with col2:
    if st.button("セクター別分析"):
        if folder_text and api_key:
            with st.spinner("分析中..."):
                model = get_model(api_key)
                prompt = f"以下の銘柄リストを業種別に分類し、今注目すべきセクターを1つだけ挙げて簡潔に理由を教えて:\n{folder_text}"
                st.session_state['sector_result'] = safe_generate(model, prompt)

if 'screen_result' in st.session_state:
    st.info(st.session_state['screen_result'])
if 'sector_result' in st.session_state:
    st.success("📊 セクター分析\n\n" + st.session_state['sector_result'])

# --- 2. 個別分析 & 対話 ---
st.markdown("### 2. 個別銘柄の分析・対話")
if 'display_list' in st.session_state:
    selected_item = st.selectbox("銘柄を選択", st.session_state['display_list'])
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if st.button("分析レポート作成"):
        st.session_state.chat_history = []
        with st.spinner("戦略策定中..."):
            model = get_model(api_key)
            prompt = f"プロトレーダーとして【{selected_item}】のアドバイスをして。リスク許容度{risk_level}、スタイル{investment_style}、逆指値の目安も含めて200文字程度で。"
            res_text = safe_generate(model, prompt)
            st.session_state.chat_history.append({"role": "assistant", "content": res_text})

    # 対話履歴の表示
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if st.session_state.chat_history:
        if user_query := st.chat_input("さらに質問..."):
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            with st.chat_message("user"): st.markdown(user_query)
            
            with st.spinner("回答中..."):
                model = get_model(api_key)
                # 履歴をすべて送ると重くなるため、直近のやり取りに絞る
                chat_context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.chat_history[-3:]])
                res_text = safe_generate(model, f"これまでの流れを踏まえて簡潔に答えて:\n{chat_context}\n質問: {user_query}")
                st.session_state.chat_history.append({"role": "assistant", "content": res_text})
                st.rerun()

# --- メモ機能 ---
st.markdown("---")
st.markdown("### 📓 投資メモ")
memo = st.text_area("気づきをメモ（ブラウザを閉じると消えます）", value=st.session_state.get("invest_memo", ""), height=100)
st.session_state.invest_memo = memo
