import streamlit as st
import google.generativeai as genai
import re

# ページ設定
st.set_page_config(page_title="プロフェッショナル株式分析", page_icon="📈")
st.title("📈 投資戦略分析システム")

# --- APIキーの設定 ---
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("Google API Keyを入力してください", type="password")

# --- 銘柄リストの解析と自動抽出 ---
st.markdown("### 1. 銘柄情報の入力")
folder_text = st.text_area(
    "日経の銘柄フォルダ等の情報をここに貼り付けてください（コード、銘柄名、株価等）", 
    height=150, 
    placeholder="例: 9759 NSD 2,844 ..."
)

if st.button("リストから銘柄を抽出する"):
    if folder_text:
        st.session_state['raw_list'] = folder_text
        
        # 【改良】コードと企業名のペアを抽出するロジック
        # 4桁の数字の後に続く日本語やアルファベットを企業名として取得
        matches = re.findall(r'(\d{4})\s+([^\s\d]+)', folder_text)
        if matches:
            # 「コード 企業名」の形式でリスト化
            st.session_state['display_list'] = [f"{m[0]} {m[1]}" for m in matches]
            st.success(f"{len(matches)}件の銘柄を検出しました。")
        else:
            # 万が一企業名が取れなかった場合はコードのみ抽出
            codes = sorted(list(set(re.findall(r'\b\d{4}\b', folder_text))))
            st.session_state['display_list'] = codes
            st.warning("企業名の特定が難しいため、コードのみリスト化しました。")
    else:
        st.warning("テキストを貼り付けてください。")

# --- 銘柄選択と自動分析 ---
if 'display_list' in st.session_state:
    st.markdown("### 2. 分析対象の選択")
    selected_item = st.selectbox("分析したい銘柄を選択してください", st.session_state['display_list'])

    if st.button(f"{selected_item} の投資戦略を生成"):
        if not api_key:
            st.error("APIキーが必要です。")
        else:
            try:
                genai.configure(api_key=api_key)
                
                # 利用可能な最新モデルを動的に取得（エラー回避）
                model_list = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                target_model_name = next((m for m in model_list if 'gemini-1.5-flash' in m), model_list[0])
                model = genai.GenerativeModel(model_name=target_model_name)
                
                with st.spinner("プロの視点で戦略を策定中..."):
                    prompt = f"""
                    あなたは百戦錬磨のプロトレーダー兼証券アナリストです。
                    以下の【リスト情報】から、選択された【{selected_item}】の最新株価を特定し、
                    詳細な投資アドバイスをしてください。

                    【リスト情報】:
                    {st.session_state['raw_list']}

                    【分析の進め方】:
                    1. 特定した「企業名」と「現在株価」をまず明示してください。
                    2. 「短期」「中期」「長期」の3つの視点で、具体的な「買い推奨価格」「利益確定ターゲット」「損切りライン」を提示してください。
                    3. 余裕資金での運用であることを踏まえ、リターンを最大化するための戦略（時間差売却やホールドの判断基準）を論理的に解説してください。

                    丁寧かつ誠実で、投資家が納得できる論理的な日本語で回答してください。
                    """
                    
                    response = model.generate_content(prompt)
                    st.session_state['analysis_output'] = response.text
                    st.session_state['selected_stock'] = selected_item

            except Exception as e:
                st.error(f"分析エラーが発生しました: {str(e)}")

# --- 分析結果の表示 ---
if 'analysis_output' in st.session_state:
    st.markdown("---")
    st.subheader(f"📊 {st.session_state['selected_stock']} 投資戦略レポート")
    st.markdown(st.session_state['analysis_output'])
    st.info("※本分析は提供されたデータに基づくAIの推論です。実際の投資判断は自己責任でお願いいたします。")
