import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import tempfile
import os
import re

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
    with st.spinner('ムー先生が全力で執筆中...'):
        try:
            # 教えていただいた成功ロジックでモデルを選択
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            target_models = ["models/gemini-1.5-flash", "models/gemini-1.5-pro", "models/gemini-pro"]
            model_name = next((m for m in target_models if m in available_models), available_models[0])
            model = genai.GenerativeModel(model_name=model_name)

            prompt = f"""
            タイ語講師「ムー先生」として【{search_query}】を解説してください。挨拶は不要です。必ず以下の3項目を含めてください。
            1. 【基本】: タイ語 | カタカナ | 日本語の意味
            2. 【成り立ち】: 語源や分解（例：A + B）の説明
            3. 【バリエーション】: 日常フレーズを2〜3個
            """

            response = model.generate_content(prompt)
            full_text = response.text

            # --- 表示抽出ロジック（強化版） ---
            # 各項目を正規表現で抜き出します
            def extract(label, text):
                # 「1. 【基本】:」のような形から次の項目までを抜き出す
                pattern = f"【{label}】:?(.*?)(?=\\n\\d|\\n【|$)"
                match = re.search(pattern, text, re.DOTALL)
                return match.group(1).strip() if match else ""

            kihon = extract("基本", full_text)
            naritachi = extract("成り立ち", full_text)
            variation = extract("バリエーション", full_text)

            # --- カード表示 ---
            # 1. 検索結果
            if kihon:
                st.markdown('<div class="dict-card">', unsafe_allow_html=True)
                st.markdown('<div class="section-header">🔍 検索結果</div>', unsafe_allow_html=True)
                st.write(kihon)
                # 音声再生
                try:
                    thai_text = kihon.split('|')[0].strip()
                    tts = gTTS(text=thai_text, lang="th")
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                        tts.save(fp.name)
                        st.audio(fp.name)
                except: pass
                st.markdown('</div>', unsafe_allow_html=True)

            # 2. 成り立ち
            if naritachi:
                st.markdown('<div class="dict-card">', unsafe_allow_html=True)
                st.markdown('<div class="section-header">🧩 言葉の成り立ち</div>', unsafe_allow_html=True)
                st.write(naritachi)
                st.markdown('</div>', unsafe_allow_html=True)

            # 3. バリエーション
            if variation:
                st.markdown('<div class="dict-card">', unsafe_allow_html=True)
                st.markdown('<div class="section-header">🚀 すぐに使える表現</div>', unsafe_allow_html=True)
                st.write(variation)
                st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

with st.sidebar:
    st.info("調べたい言葉を入れてね！ムー先生が分解して教えるよ。")
