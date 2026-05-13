import streamlit as st
import google.generativeai as genai
import re

# ページ設定
st.set_page_config(page_title="Tacoトレード", page_icon="🐙")

# 1. タイトル（赤いタコのイラスト付き）
st.title("🐙 Tacoトレード")

# --- APIキーの設定 ---
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("Google API Keyを入力してください", type="password")

# --- サイドバー：設定 ---
st.sidebar.header("分析設定")
# 2. リスク許容度（5段階）
risk_level = st.sidebar.slider("リスク許容度", 1, 5, 3, help="1:慎重 ～ 5:積極的")
# 3. 投資スタイル
investment_style = st.sidebar.multiselect(
    "重視する投資スタイル",
    ["短期（数日〜数週間）", "中期（数ヶ月〜1年）", "長期（数年以上）"],
    default=["中期（数ヶ月〜1年）"]
)

# --- 銘柄リストの入力 ---
st.markdown("### 1. 銘柄フォルダの読み込み")
folder_text = st.text_area(
    "日経の銘柄フォルダ等の情報を貼り付けてください", 
    height=100, 
    placeholder="例: 9759 プライム NSD 2,844 ..."
)

# 共通のモデル取得関数
def get_model(api_key):
    genai.configure(api_key=api_key)
    model_list = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target = next((m for m in model_list if 'gemini-1.5-flash' in m), model_list[0])
    return genai.GenerativeModel(model_name=target)

# --- 4. スクリーニング機能 ---
if st.button("全銘柄をスキャンして注目株を見つける"):
    if not folder_text or not api_key:
        st.error("リストの貼り付けとAPIキーの確認をお願いします。")
    else:
        try:
            model = get_model(api_key)
            with st.spinner("全銘柄の状態をチェックしています..."):
                screen_prompt = f"""
                以下のリストから全ての銘柄を確認し、テクニカル・ファンダメンタルズの観点から「今が買い時の銘柄」と「利益確定を検討すべき売り時の銘柄」を数銘柄ずつピックアップしてください。
                
                【リスト情報】:
                {folder_text}
                
                【回答形式】:
                落ち着いた丁寧な言葉で、以下の形式で簡潔に出力してください。
                ■ 買い時注目銘柄
                ・[コード] [企業名]：[一言理由と目安株価]
                ■ 売り時注目銘柄
                ・[コード] [企業名]：[一言理由と目安株価]
                """
                response = model.generate_content(screen_prompt)
                st.session_state['screen_result'] = response.text
                # 銘柄リストも更新
                matches = re.findall(r'(\d{4})\s+[^\s\d]+\s+([^\s\d]+)', folder_text)
                st.session_state['display_list'] = [f"{m[0]} {m[1]}" for m in matches] if matches else re.findall(r'\b\d{4}\b', folder_text)
        except Exception as e:
            st.error(f"スキャンエラー: {e}")

if 'screen_result' in st.session_state:
    st.info(st.session_state['screen_result'])

# --- 5. 銘柄選択と詳細分析 ---
st.markdown("### 2. 個別銘柄の分析")
if 'display_list' in st.session_state:
    selected_item = st.selectbox("詳しく調べたい銘柄を選んでください", st.session_state['display_list'])

    if st.button("分析レポートを作成"):
        try:
            model = get_model(api_key)
            with st.spinner("戦略を練っています..."):
                # プロンプトの改善（親しみやすい言葉・簡潔さ・設定の反映）
                prompt = f"""
                あなたは親しみやすくも有能なプロトレーダーです。
                【{selected_item}】について、以下の条件でアドバイスしてください。

                【ユーザー設定】:
                ・リスク許容度: 5段階中 {risk_level}
                ・重視するスタイル: {', '.join(investment_style)}
                ・リスト情報: {folder_text}

                【回答のルール】:
                1. 専門用語は使いつつも、親しみやすい丁寧な言葉遣いで。
                2. 内容は簡潔にポイントを絞る。ただし、具体的な「目安株価（買い・利確・損切り）」は必ず数字で出すこと。
                3. リスク許容度に応じた売買の積極性を反映させる。

                まず「結論」を述べ、その後に「各期間の戦略」を短くまとめてください。
                """
                response = model.generate_content(prompt)
                st.session_state['analysis_output'] = response.text
                st.session_state['selected_stock'] = selected_item
        except Exception as e:
            st.error(f"分析エラー: {e}")

# --- 分析結果の表示 ---
if 'analysis_output' in st.session_state:
    st.markdown("---")
    st.subheader(f"📊 {st.session_state['selected_stock']} の戦略ノート")
    st.markdown(st.session_state['analysis_output'])
    
    # 3. さらに知りたい場合の詳細表示ボタン
    if st.button("もっと詳しく（詳細分析を表示）"):
        with st.spinner("深掘りしています..."):
            model = get_model(api_key)
            detail_res = model.generate_content(f"先ほどの分析を踏まえ、{st.session_state['selected_stock']}について、業界内での立ち位置や今後の決算予定など、投資判断を後押しする詳細な情報を教えてください。")
            st.write(detail_res.text)
