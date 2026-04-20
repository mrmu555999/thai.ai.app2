import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import tempfile
import os

# --- 1. ページ設定 ---
st.set_page_config(page_title="ムー先生の深掘りタイ語辞書", page_icon="🐷", layout="centered")

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
    st.error("⚠️ APIキーを設定してください。")
    st.stop()

# --- 3. ヘッダー ---
st.markdown('<p class="main-title">ムー先生の深掘りタイ語辞書 🐷🎓</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">日本語からタイ語を、タイ文字から意味と成り立ちを調べよう！</p>', unsafe_allow_html=True)

# --- 4. 入力エリア ---
search_query = st.text_input("", placeholder="例：眠い / ง่วงนอน")

if search_query:
    with st.spinner('ムー先生が調べています...'):
        try:
            # --- 【教えていただいた自動判別ロジック】 ---
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            target_models = ["models/gemini-1.5-flash", "models/gemini-1.5-pro", "models/gemini-pro"]
            model_name = next((m for m in target_models if m in available_models), available_models[0])

            model = genai.GenerativeModel(model_name=model_name)

            prompt = f"""
            あなたはタイ語講師「ムー先生」です。キーワード【{search_query}】について解説してください。
            挨拶は不要です。

            1. 【基本】: タイ語 | カタカナ読み | 日本語の意味
            2. 【成り立ち】: 語源やパーツ分解の説明。
            3. 【バリエーション】: その言葉を使った日常フレーズを2〜3個。
            """

            response = model.generate_content(prompt)
            result_text = response.text

            # --- 表示ロジック ---
            sections = result_text.split('\n\n')

            # 🔍 検索結果
            st.markdown('<div class="dict-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="section-header">🔍 検索結果</div>', unsafe_allow_html=True)
            
            if sections:
                first_line = sections[0]
                st.write(first_line)
                
                # 音声再生
                try:
                    # タイ語部分を抜き出し
                    thai_text = first_line.split('|')[0].replace('【基本】:', '').strip()
                    tts = gTTS(text=thai_text, lang="th")
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                        tts.save(fp.name)
                        st.audio(fp.name)
                except:
                    pass
            st.markdown('</div>', unsafe_allow_html=True)

            # 🧩 詳細セクション
            for sec in sections[1:]:
                if "【成り立ち】" in sec or "【バリエーション】" in sec:
                    header = "🧩 言葉の成り立ち" if "成り立ち" in sec else "🚀 すぐに使える表現"
                    st.markdown('<div class="dict-card">', unsafe_allow_html=True)
                    st.markdown(f'<div class="section-header">{header}</div>', unsafe_allow_html=True)
                    st.write(sec)
                    st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

# --- 5. サイドバー ---
with st.sidebar:
    st.info("調べたい言葉を入力してね！")
