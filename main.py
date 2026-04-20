import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import tempfile

# --- 1. ページ設定 ---
st.set_page_config(
    page_title="ムー先生のタイ語‼️",
    page_icon="🇹🇭",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 背景色とスタイルの設定（Mr.Muカスタムスタイル）
st.markdown("""
    <style>
    .stApp { background-color: #fcfcfc; }
    .stButton>button { width: 100%; border-radius: 12px; background-color: #d93025; color: white; font-weight: bold; }
    .thai-card { background-color: white; padding: 18px; border-radius: 15px; border-left: 8px solid #d93025; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 20px; }
    .thai-word { font-size: 32px; font-weight: bold; color: #1a1a1a; }
    .thai-mean { font-size: 22px; font-weight: bold; color: #d93025; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. セキュリティ設定 ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        API_KEY = st.secrets["GEMINI_API_KEY"]
    else:
        API_KEY = "dummy"
    genai.configure(api_key=API_KEY)
except Exception as e:
    st.error("APIキーの設定を確認してください。")
    st.stop()

# --- 3. メイン画面 ---

col1, col2, col3 = st.columns([1,2,1])

with col2:
    st.image("musenseinew.jpg", width=400)

st.markdown("""
<div style='text-align:center;'>

<h1 style="margin-bottom:0;">
ムー先生<span style="font-size:0.8em;">の</span>タイ語レッスン🇹🇭
</h1>

<div style='font-size:1.1rem; font-weight:bold; margin-top:20px;'>

タイ旅行の前にサクッと予習 ✏️<br>

シチュエーションを入力すると<br>
その場で使えるタイ語フレーズを 🇹🇭💬<br>
ムー先生が生成します 🐷🎓✨

</div>

</div>
""", unsafe_allow_html=True)

# 入力欄
situation = st.text_area(
    "",
    placeholder="""入力例：
屋台でカオマンガイを食べる
タイマッサージに行く
⚪︎⚪︎⚪︎へ飲みに行く""",
    height=150
)

# --- タイカラーのボタンデザイン ---
st.markdown("""
<style>
div.stButton > button {
    background: linear-gradient(90deg, #d50000, #0033a0);
    color: white;
    font-weight: bold;
    border-radius: 12px;
    border: 2px solid #ffffff;
    height: 3.5em;
    font-size: 18px;
}

div.stButton > button:hover {
    background: linear-gradient(90deg, #0033a0, #d50000);
    border: 2px solid #ffd700;
}
</style>
""", unsafe_allow_html=True)

# --- 4. 生成ロジック ---
if st.button("フレーズを生成する！", use_container_width=True):

    if not situation:
        st.warning("シチュエーションを入力してくださいね！")

    else:
        with st.spinner('ムー先生AIが作成中...'):

            try:

                # 利用可能なモデルを自動判別
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                target_models = ["models/gemini-1.5-flash", "models/gemini-1.5-pro", "models/gemini-pro"]
                model_name = next((m for m in target_models if m in available_models), available_models[0])

                model = genai.GenerativeModel(model_name=model_name)

                # 【Mr.Mu流：深掘りシミュレーション型プロンプト】
                prompt = f"""
あなたはタイ文化、タイ語の日常会話、観光事情、日本人旅行者の行動を熟知したプロのタイ語コミュニケーションガイドです。

ユーザーが入力したシチュエーション：
【{situation}】

この場面で日本人旅行者がタイ人と実際に会話する状況を具体的に想像してください。

まず頭の中で、このシチュエーションで発生する会話パターンを考えてください。

例：
・挨拶
・質問
・注文
・値段確認
・お願い
・確認
・感謝
・断る
・支払い
・トラブル対応

次に、その場面で実際に使う可能性が高いタイ語を作成してください。

【夜の繁華街シチュエーション判断】

ユーザーのシチュエーションに次のようなタイの夜の繁華街の名称が含まれている場合：

ナナプラザ  
ソイカウボーイ   
タニヤ  
テーメーカフェ  

さらに次のような行動や言葉が含まれている場合：

飲む  
バー  
飲みに行く  
夜遊び  
ゴーゴーバー  

この場合、日本人旅行者が女性がいるお店で会話している状況を想定してください。

そして会話例文の中に必ず次の意味の例文を1つ含めてください。

「LINEを交換しましょう」

この例文は21〜40行の会話例文の中に必ず含めてください。

【出力内容】

・最初の20行：この場面でよく使うタイ語の単語  
（単語または短いフレーズ）

・次の20行：この場面で実際に使う短い例文  
（旅行者がそのまま使える自然な会話）

【条件】

・タイ人が日常会話で使う自然な表現  
・タイ語はタイ人ネイティブが日常で実際に使う自然な会話のみ生成してください  
・書き言葉ではなく会話で使う口語表現を優先してください  
・日本人旅行者でも使いやすい  
・丁寧な表現（男性語尾：ครับ / krap を使用）  
・単語と例文は重複しない  
・観光・生活で実際に使う会話を優先  
・教科書的な不自然な表現は避ける  
・カタカナは日本人が読みやすい自然なカタカナ表記にしてください  
・カタカナにアルファベット（a〜z）は絶対に含めないでください  
・例：ครับ → クラップ  

【出力形式】

必ず40行のみ出力してください。

1〜20行：単語または短いフレーズ  
21〜40行：短い会話例文  

各行は必ず次の形式で出力してください。

タイ語 | ローマ字 | カタカナ | 日本語

説明文は禁止  
番号は禁止  
40行のデータのみ出力

例：

สวัสดีครับ | sa-wat-dii krap | サワッディー クラップ | こんにちは
ขอบคุณครับ | khop-khun krap | コープクン クラップ | ありがとう
ราคาเท่าไร | raa-khaa thao-rai | ラーカー タオライ | いくらですか

"""

                response = model.generate_content(prompt)

                lines = response.text.split('\n')

                count = 0
                copy_text = ""

                for line in lines:

                    if "|" not in line:
                        continue

                    parts = [p.strip() for p in line.split("|")]

                    if len(parts) < 4:
                        continue

                    count += 1

                    thai = parts[0]
                    roma = parts[1]
                    kana = parts[2]
                    jp = parts[3]

                    copy_text += f"{count}. {thai} ({roma}) : {jp}\n"

                    if count == 1:
                        st.markdown("### ✏️ 【単語・フレーズ 20】")
                        st.divider()

                    if count == 21:
                        st.write("")
                        st.markdown("### 📚 【会話例文 20】")
                        st.divider()

                    card_html = f'''
<div class="thai-card">
    <div class="thai-word">{count}. {thai}</div>
    <div style="color: #666;">{roma} / {kana}</div>
    <div class="thai-mean">&#128073; {jp}</div>
</div>
'''

                    st.markdown(card_html, unsafe_allow_html=True)

                    try:
                        tts = gTTS(text=thai, lang="th")
                        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                        tts.save(tmp.name)
                        st.audio(tmp.name)
                    except:
                        pass

                    st.code(thai, language="text")

                if count != 40:
                    st.warning(f"⚠ 出力行数が40ではありません（現在 {count} 行）")

                st.divider()
                st.subheader("📋 スマホへのメモ用")
                st.write("必要な方はコピーしてご活用ください。")
                st.text_area("", value=copy_text, height=400, key="copy_area_final")

            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

# --- 5. フッター ---
st.divider()
st.markdown("<div style='text-align: center; color: gray;'>Presented by Mr.Mu</div>", unsafe_allow_html=True)
