import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="タコ・トレード", page_icon="🐙")
st.title("🐙 タコ・トレード分析室")

# --- APIキーの設定 ---
# 1. Secretsにあるか確認、なければサイドバーから入力
api_key = st.secrets.get("OPENAI_API_KEY") or st.sidebar.text_input("OpenAI API Key", type="password")

stock_code = st.text_input("分析したい銘柄コードを入力（例: 9759）", value="9759")

if st.button("タコ足分析を開始する"):
    if not api_key:
        st.error("APIキーが設定されていません。Secretsに登録するかサイドバーに入力してください。")
    else:
        client = OpenAI(api_key=api_key)
        
        with st.spinner('タコの足が情報を収集しています...'):
            try:
                prompt = f"""
                あなたは優秀なトレーダー「タコ」です。
                銘柄コード【{stock_code}】について、以下の3つの視点からプロの分析を行ってください。

                1. 【ファンダメンタルの足】: 業績、配当、成長性について
                2. 【テクニカルの足】: 現在の株価水準、売り時・買い時の目安
                3. 【慎重・空売りの足】: 最悪のシナリオ（リスク要因）と損切りポイント

                最後に、中長期的な「総合評価」をタコらしくユーモアを交えて結論づけてください。
                """

                response = client.chat.completions.create(
                    model="gpt-4o", 
                    messages=[{"role": "user", "content": prompt}]
                )
                
                st.markdown("---")
                st.subheader(f"📊 銘柄コード {stock_code} の分析結果")
                st.write(response.choices[0].message.content)
                
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
