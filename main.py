import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="タコ・トレード", page_icon="🐙")
st.title("🐙 タコ・トレード分析室")

# サイドバーで設定
st.sidebar.header("設定")
api_key = st.sidebar.text_input("OpenAI API Key", type="password")

stock_code = st.text_input("分析したい銘柄コードを入力（例: 9759）", value="9759")

if st.button("タコ足分析を開始する"):
    if not api_key:
        st.error("APIキーを入力してください。")
    else:
        client = OpenAI(api_key=api_key)
        
        with st.spinner('タコの足が情報を収集しています...'):
            try:
                # AIへの命令文（プロンプト）
                prompt = f"""
                あなたは優秀なトレーダー「タコ」です。
                銘柄コード【{stock_code}】について、以下の3つの視点からプロの分析を行ってください。

                1. 【ファンダメンタルの足】: 業績、配当、成長性について
                2. 【テクニカルの足】: 現在の株価水準、売り時・買い時の目安
                3. 【慎重・空売りの足】: 最悪のシナリオ（リスク要因）と損切りポイント

                最後に、中長期的な「総合評価」をタコらしくユーモアを交えて結論づけてください。
                """

                response = client.chat.completions.create(
                    model="gpt-4o",  # または gpt-3.5-turbo
                    messages=[{"role": "user", "content": prompt}]
                )
                
                # 結果を表示
                st.markdown("---")
                st.subheader(f"📊 銘柄コード {stock_code} の分析結果")
                st.write(response.choices[0].message.content)
                
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
