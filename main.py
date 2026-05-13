import streamlit as st
import google.generativeai as genai
import re
import time # 追加

# ページ設定
st.set_page_config(page_title="Tacoトレード", page_icon="🐙")
st.title("🐙 Tacoトレード")

# --- APIキーの設定 ---
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("Google API Keyを入力してください", type="password")

# --- サイドバー設定 ---
st.sidebar.header("分析設定")
risk_level = st.sidebar.slider("リスク許容度", 1, 5, 3)
investment_style = st.sidebar.multiselect("スタイル", ["短期", "中期", "長期"], default=["中期"])

def get_model(api_key):
    genai.configure(api_key=api_key)
    model_list = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target = next((m for m in model_list if 'gemini-1.5-flash' in m), model_list[0])
    return genai.GenerativeModel(model_name=target)

# --- 分析実行用ヘルパー（エラー回避付き） ---
def safe_generate(model, prompt):
    try:
        return model.generate_content(prompt).text
    except Exception as e:
        if "429" in str(e) or "ResourceExhausted" in str(e):
            return "⚠️【回数制限エラー】現在リクエストが集中しています。1分ほど待ってから再度お試しください。"
        return f"⚠️ エラーが発生しました: {str(e)}"

# --- 1. 銘柄フォルダの読み込み ---
st.markdown("### 1. 銘柄フォルダの読み込み")
folder_text = st.text_area("日経銘柄フォルダ情報を貼り付け", height=100, key="folder_input")

col1, col2 = st.columns(2)
with col1:
    if st.button("全銘柄をスキャン"):
        if folder_text and api_key:
            with st.spinner("スキャン中..."):
                model = get_model(api_key)
                prompt = f"以下の銘柄リストから買い・売りの注目株を簡潔に抽出して:\n{folder_text}"
                st.session_state['screen_result'] = safe_generate(model, prompt)
                matches = re.findall(r'(\d{4})\s+[^\s\d]+\s+([^\s\d]+)', folder_text)
                st.session_state['display_list'] = [f"{m[0]} {m[1]}" for m in matches] if matches else re.findall(r'\b\d{4}\b', folder_text)

with col2:
    if st.button("セクター別分析"):
        if folder_text and api_key:
            with st.spinner("分析中..."):
                model = get_model(api_key)
                prompt = f"以下の銘柄リストを業種別に分類し、勢いや注意点を簡潔に分析して:\n{folder_text}"
                st.session_state['sector_result'] = safe_generate(model, prompt)

if 'screen_result' in st.session_state:
    st.info(st.session_state['screen_result'])
if 'sector_result' in st.session_state:
    st.success("📊 セクター分析結果\n\n" + st.session_state['sector_result'])

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
            prompt = f"プロトレーダーとして【{selected_item}】のアドバイスをして。リスク許容度{risk_level}、スタイル{investment_style}、逆指値の目安も含めて簡潔に。"
            res_text = safe_generate(model, prompt)
            st.session_state.chat_history.append({"role": "assistant", "content": res_text})

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if st.session_state.chat_history:
        if user_query := st.chat_input("さらに質問..."):
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            with st.chat_message("user"): st.markdown(user_query)
            
            with st.spinner("回答中..."):
                model = get_model(api_key)
                chat_context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.chat_history])
                res_text = safe_generate(model, f"対話履歴を踏まえて回答して:\n{chat_context}")
                st.session_state.chat_history.append({"role": "assistant", "content": res_text})
                with st.chat_message("assistant"): st.markdown(res_text)

# --- メモ機能 ---
st.markdown("---")
st.markdown("### 📓 投資メモ")
memo = st.text_area("気づきをメモ", value=st.session_state.get("invest_memo", ""), height=100)
st.session_state.invest_memo = memo
if st.button("保存"): st.success("保存しました。")
