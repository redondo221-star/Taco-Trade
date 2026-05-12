import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="タコ・トレード", page_icon="🐙")
st.title("🐙 タコ・トレード分析室")

# --- 設定（サイドバー） ---
st.sidebar.header("設定")
api_key = (st.secrets.get("GEMINI_API_KEY") or 
           st.sidebar.text_input("Google API Key", type="password"))

# --- メイン画面 ---
stock_code = st.text_input("分析したい銘柄コードを入力（例: 9759）", value="9759")

if st.button("タコ足分析を開始する"):
    if not api_key:
        st.error("APIキーを入力してください。")
    else:
        try:
            genai.configure(api_key=api_key)
            
            # 【究極の対策】利用可能なモデルを自動で検索して、最初に見つかった動くモデルを使う
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            if not available_models:
                st.error("利用可能なモデルが見つかりませんでした。APIキーの権限を確認してください。")
            else:
                # 優先的に使いたいモデルを探す（flashがあればそれを、なければ最初に見つかったものを採用）
                target_model = next((m for m in available_models if 'flash' in m), available_models[0])
                model = genai.GenerativeModel(model_name=target_model)
                
                with st.spinner(f'タコが {target_model} を使って {stock_code} を調査中...'):
                    prompt = f"""
                    あなたは凄腕トレーダー「タコ」です。
                    銘柄コード【{stock_code}】について、以下の3点からプロの分析を行ってください。
                    1. 【ファンダメンタル】業績・配当
                    2. 【テクニカル】売り時・買い時
                    3. 【慎重派の視点】リスク要因
                    結論はタコらしくユーモア（語尾に「〜だタコ」など）を交えて日本語で回答してください。
                    """
                    
                    response = model.generate_content(prompt)
                    
                    st.markdown("---")
                    st.subheader(f"📊 {stock_code} の分析結果")
                    st.write(response.text)
                    st.info(f"（使用中のモデル: {target_model}）")
                
        except Exception as e:
            st.error(f"タコの足がもつれました: {str(e)}")
            st.info("APIキーを正しく入力し、Enterを押してからボタンをクリックしてください。")
