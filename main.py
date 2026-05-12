import streamlit as st
import google.generativeai as genai

# ページ設定
st.set_page_config(page_title="株価分析アシスタント", page_icon="📈")
st.title("📈 株価分析システム")

# --- APIキーの設定 ---
# Secretsから自動取得、なければサイドバーを表示
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("Google API Keyを入力してください", type="password")

# --- メイン画面 ---
st.markdown("指定した銘柄コードについて、AIが多角的な分析を行います。")
stock_code = st.text_input("分析したい銘柄コード（4桁）", value="9759")

if st.button("分析を実行する"):
    if not api_key:
        st.error("APIキーが設定されていません。StreamlitのSecretsに登録するか、サイドバーに入力してください。")
    else:
        try:
            genai.configure(api_key=api_key)
            
            # 利用可能なモデルを自動取得
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            target_model = next((m for m in available_models if 'flash' in m), available_models[0])
            model = genai.GenerativeModel(model_name=target_model)
            
            with st.spinner(f"銘柄コード {stock_code} を分析しています。少々お待ちください..."):
                prompt = f"""
                あなたはプロの証券アナリストです。
                銘柄コード【{stock_code}】について、以下の項目に沿って論理的かつ丁寧に分析してください。

                1. 【ファンダメンタル分析】: 業績の推移、配当利回り、企業の成長性について
                2. 【テクニカル分析】: 現在の株価チャートの傾向、買い時・売り時の考察
                3. 【リスク要因】: 投資する際に注意すべき懸念点や損切り目安

                最後に、中長期的な視点での総合的な評価を述べてください。
                回答は落ち着いた、信頼感のある日本語でお願いします。
                """
                
                response = model.generate_content(prompt)
                
                st.markdown("---")
                st.subheader(f"📊 銘柄コード {stock_code} 分析レポート")
                st.write(response.text)
                
        except Exception as e:
            st.error(f"分析中にエラーが発生しました: {str(e)}")
            st.info("APIキーの設定や通信環境を確認してください。")
