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
risk_level = st.sidebar.slider("リスク許容度", 1, 5, 3)
investment_style = st.sidebar.multiselect("スタイル", ["短期", "中期", "長期"], default=["中期"])

def get_model(api_key):
    genai.configure(api_key=api_key)
    try:
        return genai.GenerativeModel(model_name="gemini-2.0-flash")
    except:
        return genai.GenerativeModel(model_name="gemini-1.5-flash")

def safe_generate(model, prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "ResourceExhausted" in error_msg:
            return "⚠️【回数制限】1分待つか、別プロジェクトのAPIキーをお試しください。"
        return f"⚠️ エラーが発生しました: {error_msg}"

# --- 1. 銘柄情報の入力 ---
st.markdown("### 1. 銘柄情報の入力")

# 【改善】直接入力と一括貼り付けの両方に対応
input_mode = st.radio("入力方法を選択", ["銘柄を直接指定（1銘柄）", "フォルダから一括読み込み（複数銘柄）"], horizontal=True)

if input_mode == "銘柄を直接指定（1銘柄）":
    direct_input = st.text_input("企業名や銘柄コードを入力してください", placeholder="例: トヨタ、9759、ソフトバンクグループ")
    if direct_input:
        st.session_state['display_list'] = [direct_input]
        st.session_state['raw_list'] = direct_input

else:
    folder_text = st.text_area("日経銘柄フォルダ情報を貼り付け", height=100, key="folder_input")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("リストを解析・スキャン"):
            if folder_text and api_key:
                st.session_state['raw_list'] = folder_text
                with st.spinner("スキャン中..."):
                    model = get_model(api_key)
                    prompt = f"以下の銘柄リストから買い・売りの注目株を抽出して:\n{folder_text}"
                    st.session_state['screen_result'] = safe_generate(model, prompt)
                    
                    # 抽出ロジックの強化：コード＋名前に加え、名前のみの行も拾う
                    matches = re.findall(r'(\d{4})\s+[^\s\d]+\s+([^\s\d]+)', folder_text) # 日経形式
                    if not matches:
                        matches = re.findall(r'(\d{4})', folder_text) # コードのみ
                    
                    if matches:
                        st.session_state['display_list'] = [f"{m[0]} {m[1]}" if isinstance(m, tuple) else m for m in matches]
                    else:
                        # 最終手段：改行ごとにリスト化
                        st.session_state['display_list'] = [line.strip() for line in folder_text.split('\n') if line.strip()]

    with col2:
        if st.button("セクター別分析"):
            if folder_text and api_key:
                with st.spinner("分析中..."):
                    model = get_model(api_key)
                    prompt = f"以下の銘柄リストの業種別傾向を分析して:\n{folder_text}"
                    st.session_state['sector_result'] = safe_generate(model, prompt)

    if 'screen_result' in st.session_state:
        st.info(st.session_state['screen_result'])
    if 'sector_result' in st.session_state:
        st.success("📊 セクター分析\n\n" + st.session_state['sector_result'])

# --- 2. 個別分析 & 対話 ---
st.markdown("---")
st.markdown("### 2. 個別銘柄の分析・対話")

if 'display_list' in st.session_state and st.session_state['display_list']:
    selected_item = st.selectbox("分析対象を選択", st.session_state['display_list'])
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if st.button("分析レポート作成"):
        st.session_state.chat_history = []
        with st.spinner("戦略策定中..."):
            model = get_model(api_key)
            # リスト情報がある場合とない場合でプロンプトを分ける
            context = st.session_state.get('raw_list', '')
            prompt = f"""
            プロトレーダーとして【{selected_item}】のアドバイスをして。
            条件: リスク許容度{risk_level}, スタイル{investment_style}
            背景データ: {context}
            
            【回答内容】:
            1. 結論と売買戦略
            2. 目標株価と逆指値（損切り）の目安
            3. 注意点（簡潔に）
            """
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
                chat_context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.chat_history[-3:]])
                res_text = safe_generate(model, f"対話履歴を踏まえて回答して:\n{chat_context}\n質問: {user_query}")
                st.session_state.chat_history.append({"role": "assistant", "content": res_text})
                st.rerun()

# --- 投資メモ ---
st.markdown("---")
st.markdown("### 📓 投資メモ")
memo = st.text_area("気づきをメモ", value=st.session_state.get("invest_memo", ""), height=100)
st.session_state.invest_memo = memo
