import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import tempfile
import os

# --- 1. ページ設定 ---
st.set_page_config(
    page_title="ムー先生の深掘りタイ語辞書",
    page_icon="🐷",
    layout="centered"
)

# カスタムCSS
st.markdown("""
    <style>
    .main-title { font-size: 2.2rem; font-weight: bold; color: #d93025; text-align: center; }
    .sub-title { font-size: 1rem; color: #666; text-align: center; margin-bottom: 2rem; }
    .dict-card { background-color: white; padding: 20px; border-radius: 15px; border-left: 8px solid #0033a0; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 20px; }
    .section-header { font-size: 1.2rem; font-weight: bold; color: #d93025; margin-bottom: 10px; border-bottom: 1px solid #eee; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. API設定 ---
api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("⚠️ APIキーが設定されていません。RenderのEnvironment設定を確認してください。")
    st.stop()

# --- 3. ヘッダー ---
st.markdown('<p class="main-title">ムー先生の深掘りタイ語辞書 🐷🎓</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">日本語からタイ語を、タイ文字から意味と成り立ちを調べよう！</p>', unsafe_allow_html=True)

# --- 4. 入力エリア ---
search_query = st.text_input("", placeholder="例：眠い / ง่วงนอน", help="日本語またはタイ語を入力してください")

if search_query:
    with st.spinner('ムー先生が調べています...'):
        try:
            # 【重要】エラー回避のため、最も安定している gemini-pro を直接指定します
            model = genai.GenerativeModel("gemini-pro")
            
            prompt = f"""
            あなたはタイ語と日本語のバイリンガル講師「ムー先生」です。
            ユーザーが入力したキーワード【{search_query}】について、以下の形式で解説を生成してください。

            1. 【基本】: タイ語 | カタカナ読み | 日本語の意味
            2. 【成り立ち】: 単語を最小単位に分解して、それぞれの意味を説明。
            3. 【バリエーション】: その単語を使った日常フレーズを2〜3個。

            【出力ルール】
            ・必ず「タイ語 | カタカナ | 日本語訳」の形式を含めること。
            ・丁寧な男性表現（ครับ / krap）を使用。
            ・余計な挨拶は不要。
            """

            response = model.generate_content(prompt)
            result_text = response.text

            # --- 表示ロジック ---
            sections = result_text.split('\n\n')

            # メイン結果
            st.markdown('<div class="dict-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="section-header">🔍 検索結果</div>', unsafe_allow_html=True)
            
            first_line = sections[0]
            st.write(first_line)
            
            # 音声生成
            try:
                thai_part = first_line.split('|')[0]
                thai_text = thai_part.split(':')[-1].strip()
                
                tts = gTTS(text=thai_text, lang="th")
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                    tts.save(fp.name)
                    st.audio(fp.name)
            except:
                pass
            st.markdown('</div>', unsafe_allow_html=True)

            # 詳細セクション
            for sec in sections[1:]:
                if any(x in sec for x in ["【成り立ち】", "🧩"]):
                    header = "🧩 言葉の成り立ち"
                elif any(x in sec for x in ["【バリエーション】", "🚀"]):
                    header = "🚀 すぐに使える表現"
                else:
                    continue

                st.markdown('<div class="dict-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="section-header">{header}</div>', unsafe_allow_html=True)
                content = sec.split('】:')[-1] if '】:' in sec else sec
                st.write(content)
                st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            # 具体的なエラーメッセージを表示
            st.error(f"ムー先生が困っています: {e}")

# --- 5. 使い方ガイド ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/thailand-circular.png", width=80)
    st.title("使い方ガイド")
    st.info("調べたい言葉を入力してね！発音も聞けるよ。")
    st.divider()
    st.caption("Presented by Mr.Mu")
