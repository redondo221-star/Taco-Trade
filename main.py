import streamlit as st
import google.generativeai as genai
import re

# ページ設定
st.set_page_config(page_title="Tacoトレード", page_icon="🐙")

# 1. タイトル
st.title("🐙 Tacoトレード")

# --- APIキーの設定 ---
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("Google API Keyを入力してください", type="password")

# --- サイドバー：設定 ---
st.sidebar.header("分析設定")
risk_level = st.sidebar.slider("リスク許容度", 1, 5, 3, help="1:慎重 ～ 5:積極的")
investment_style = st.sidebar.multiselect(
    "重視するスタイル",
    ["短期", "中期", "長期"],
    default=["中期"]
)

# 共通モデル取得関数
def get_model(api_key):
    genai.configure(api_key=api_key)
    model_list = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target = next((m for m in model_list if 'gemini-1.5-flash' in m), model_list[0])
    return genai.GenerativeModel(model_name=target)

# --- 1. 銘柄フォルダの読み込み ---
st.markdown("### 1. 銘柄フォルダの読み込み")
folder_text = st.text_area(
    "日経の銘柄フォルダ情報を貼り付けてください", 
    height=100, 
    key="folder_input"
)

col1, col2 = st.columns(2)
with col1:
    if st.button("全銘柄をスキャン"):
        if folder_text and api_key:
            model = get_model(api_key)
            with st.spinner("スキャン中..."):
                screen_prompt = f"以下のリストから、買い・売りの注目株を簡潔に抽出して:\n{folder_text}"
                response = model.generate_content(screen_prompt)
                st.session_state['screen_result'] = response.text
                matches = re.findall(r'(\d{4})\s+[^\s\d]+\s+([^\s\d]+)', folder_text)
                st.session_state['display_list'] = [f"{m[0]} {m[1]}" for m in matches] if matches else re.findall(r'\b\d{4}\b', folder_text)

# --- 新機能1: セクター別分析 ---
with col2:
    if st.button("セクター別の傾向を分析"):
        if folder_text and api_key:
            model = get_model(api_key)
            with st.spinner("セクター分析中..."):
                sector_prompt = f"以下のリストにある銘柄をセクター（業種）別に分類し、今どの業界に勢いがあるか、または注意が必要なセクターはどれか分析して:\n{folder_text}"
                sector_res = model.generate_content(sector_prompt)
                st.session_state['sector_result'] = sector_res.text

if 'screen_result' in st.session_state:
    st.info(st.session_state['screen_result'])
if 'sector_result' in st.session_state:
    st.success("📊 セクター分析結果\n\n" + st.session_state['sector_result'])

# --- 2. 個別銘柄の分析 & 対話機能 ---
st.markdown("### 2. 個別銘柄の分析・対話")
if 'display_list' in st.session_state:
    selected_item = st.selectbox("銘柄を選択", st.session_state['display_list'])

    # チャット履歴の初期化
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if st.button("分析レポートを作成"):
        st.session_state.chat_history = [] # 新しい銘柄の時は履歴リセット
        try:
            model = get_model(api_key)
            # 新機能4: 逆指値の目安を含める指示
            prompt = f"""
            プロトレーダーとして【{selected_item}】のアドバイスをして。
            条件: リスク許容度{risk_level}, スタイル{investment_style}
            リスト背景: {folder_text}
            
            【必須項目】:
            1. 結論と売買戦略（簡潔に）
            2. 短期・中期・長期のターゲット株価
            3. 逆指値（損切り）をする場合の具体的な設定株価の目安とその理由
            """
            response = model.generate_content(prompt)
            st.session_state.chat_history.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"エラー: {e}")

    # 対話機能のUI
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if st.session_state.chat_history:
        if user_query := st.chat_input("この銘柄についてさらに質問（例：今の逆指値をもっと攻めるなら？）"):
            with st.chat_message("user"):
                st.markdown(user_query)
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            
            model = get_model(api_key)
            # 履歴を踏まえた回答を生成
            chat_context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.chat_history])
            res = model.generate_content(f"これまでの対話を踏まえて答えて:\n{chat_context}\nuser: {user_query}")
            
            with st.chat_message("assistant"):
                st.markdown(res.text)
            st.session_state.chat_history.append({"role": "assistant", "content": res.text})

# --- 新機能2: メモ機能 ---
st.markdown("---")
st.markdown("### 📓 投資メモ（自分専用）")
if "invest_memo" not in st.session_state:
    st.session_state.invest_memo = ""

memo_input = st.text_area("分析結果や気づいた戦略をメモしておけます（ブラウザを閉じると消去されます）", 
                          value=st.session_state.invest_memo, height=100)
st.session_state.invest_memo = memo_input
if st.button("メモを保存（確定）"):
    st.success("メモを一時保存しました。")
