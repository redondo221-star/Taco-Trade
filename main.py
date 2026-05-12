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
        st.success("リストを読み込みました。下のメニューから銘柄を選んでください。")
    else:
        st.warning("テキストを貼り付けてください。")

# --- 銘柄選択と自動分析 ---
if 'raw_list' in st.session_state:
    st.markdown("### 2. 分析対象の選択")
    codes = sorted(list(set(re.findall(r'\b\d{4}\b', st.session_state['raw_list']))))
    selected_code = st.selectbox("分析したい銘柄を選択してください", codes)

    if st.button(f"{selected_code} の投資戦略を生成"):
        if not api_key:
            st.error("APIキーが必要です。")
        else:
            try:
                genai.configure(api_key=api_key)
                
                # エラー回避のため、利用可能な最新モデルを動的に取得
                model_list = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                target_model_name = next((m for m in model_list if 'gemini-1.5-flash' in m), model_list[0])
                model = genai.GenerativeModel(model_name=target_model_name)
                
                with st.spinner("プロの視点で戦略を策定中..."):
                    prompt = f"""
                    あなたは百戦錬磨のプロトレーダー兼証券アナリストです。
                    以下の【リスト情報】から、銘柄コード【{selected_code}】の企業名と現在株価を特定し、
                    私の投資状況に合わせた詳細なアドバイスをしてください。

                    【リスト情報】:
                    {st.session_state['raw_list']}

                    【分析の進め方】:
                    1. 特定した「企業名」と「現在株価」をまず明示してください。
                    2. 「短期」「中期」「長期」の3つの視点で、具体的な「買い時」「売り時」の価格を提示してください。
                    3. 特に「売り時」については、利益確定のタイミングと、リスク回避のための損切りラインを論理的に解説してください。
                    4. 余裕資金での運用であることを踏まえ、リターンを最大化するための「時間差売却」などのテクニックも提案してください。

                    丁寧かつ誠実で、投資家が納得できる論理的な日本語で回答してください。
                    """
                    
                    response = model.generate_content(prompt)
                    st.session_state['analysis_output'] = response.text
                    st.session_state['selected_stock'] = selected_code

            except Exception as e:
                st.error(f"分析エラーが発生しました。別のモデルでの試行を推奨します: {str(e)}")

# --- 分析結果の表示 ---
if 'analysis_output' in st.session_state:
    st.markdown("---")
    st.subheader(f"📊 {st.session_state['selected_stock']} 投資戦略レポート")
    st.markdown(st.session_state['analysis_output'])
    st.info("※本分析は提供されたデータに基づくAIの推論です。実際の投資判断は自己責任でお願いいたします。")
