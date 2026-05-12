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
    "日経の銘柄フォルダ等の情報をここに貼り付けてください（銘柄コード、企業名、株価が含まれるテキスト）", 
    height=150, 
    placeholder="例: 9759 NSD 2,844 ..."
)

# 解析ボタン
if st.button("リストから銘柄を抽出する"):
    if folder_text:
        # 4桁の数字（銘柄コード）を抽出
        codes = re.findall(r'\b\d{4}\b', folder_text)
        # テキスト全体をAIに渡して、銘柄と株価の対応表を作らせる（一時保存）
        st.session_state['raw_list'] = folder_text
        st.success(f"{len(set(codes))}件の銘柄コードを検出しました。")
    else:
        st.warning("テキストを貼り付けてください。")

# --- 銘柄選択と自動分析 ---
if 'raw_list' in st.session_state:
    st.markdown("### 2. 分析対象の選択")
    # 抽出されたコードから選択
    codes = sorted(list(set(re.findall(r'\b\d{4}\b', st.session_state['raw_list']))))
    selected_code = st.selectbox("分析したい銘柄を選択してください", codes)

    if st.button(f"{selected_code} の投資戦略を生成"):
        if not api_key:
            st.error("APIキーが必要です。")
        else:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                with st.spinner("最新データを照合し、戦略を策定中..."):
                    # 貼り付けたテキスト全体を「コンテキスト」として渡し、その中の株価を特定させる
                    prompt = f"""
                    以下の【リスト情報】の中から、銘柄コード【{selected_code}】に関連する企業名と現在の株価を特定してください。
                    その上で、プロのアナリストとして詳細な投資戦略を作成してください。

                    【リスト情報】:
                    {st.session_state['raw_list']}

                    【回答の構成】:
                    1. 企業名と特定した現在株価の確認
                    
                    2. ■ 短期戦略（数日〜数週間）
                       - テクニカル指標に基づいた具体的な「買い推奨価格」「利確目標」「損切りライン」を明示。
                    
                    3. ■ 中期戦略（数ヶ月〜1年）
                       - 業績、材料、市場環境を踏まえた「目標株価」と「投資シナリオ」。
                    
                    4. ■ 長期戦略（数年以上）
                       - 事業の将来性、配当維持力、持続的成長の観点からの「保有方針」。

                    専門用語を適切に使いつつ、論理的で納得感のある解説を日本語で行ってください。
                    """
                    
                    response = model.generate_content(prompt)
                    st.session_state['analysis_output'] = response.text
                    st.session_state['selected_stock'] = selected_code

            except Exception as e:
                st.error(f"分析エラー: {str(e)}")

# --- 分析結果の表示 ---
if 'analysis_output' in st.session_state:
    st.markdown("---")
    st.subheader(f"📊 {st.session_state['selected_stock']} 投資戦略レポート")
    st.markdown(st.session_state['analysis_output'])
    
    # 投資判断に役立つ補足
    st.caption("※本分析は提供されたデータとAIの推論に基づくものであり、実際の投資は自己責任で行ってください。")
