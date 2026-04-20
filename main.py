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
    with st.spinner('ムー先生が全力で調査中...'):
        try:
            # --- 【重要】エラー回避ロジック ---
            # 利用可能な全モデルを取得し、'gemini'という名前が含まれるものを探す
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            # 優先順位をつけてモデルを選択
            target_models = ["models/gemini-1.5-flash", "models/gemini-1.5-pro", "models/gemini-pro"]
            selected_model = next((m for m in target_models if m in models), models[0])
            
            model = genai.GenerativeModel(selected_model)
            
            prompt = f"""
            タイ語講師「ムー先生」として、【{search_query}】を解説してください。挨拶は不要です。
            
            【基本】: タイ語 | カタカナ | 日本語の意味
            【成り立ち】: 語源や分解（例：A + B）
            【例文】: タイ語例文 | カタカナ | 意味
            """

            response = model.generate_content(prompt)
            full_text = response.text

            # --- 表示抽出ロジック ---
            def get_section(label, text):
                pattern = f"【{label}】:(.*?)(?=\\n【|$)"
                match = re.search(pattern, text, re.DOTALL)
                return match.group(1).strip() if match else ""

            kihon = get_section("基本", full_text)
            naritachi = get_section("成り立ち", full_text)
            reibun = get_section("例文", full_text)

            if kihon:
                st.markdown(f'<div class="dict-card"><div class="section-header">🔍 検索結果</div>{kihon}', unsafe_allow_html=True)
                try:
                    thai_text = kihon.split('|')[0].strip()
                    tts = gTTS(text=thai_text, lang="th")
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                        tts.save(fp.name)
                        st.audio(fp.name)
                except: pass
                st.markdown('</div>', unsafe_allow_html=True)

            if naritachi:
                st.markdown(f'<div class="dict-card"><div class="section-header">🧩 言葉の成り立ち</div>{naritachi}</div>', unsafe_allow_html=True)

            if reibun:
                st.markdown(f'<div class="dict-card"><div class="section-header">🚀 すぐに使える表現</div>{reibun}</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"ムー先生の通信エラー: {e}")

with st.sidebar:
    st.info("調べたい言葉を入力してね！")
