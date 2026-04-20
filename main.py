import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import tempfile
import os
import re

# --- 1. ページ設定 ---
st.set_page_config(page_title="ムー先生のタイ語‼️", page_icon="🇹🇭", layout="centered")

# 初代デザインの完全移植
st.markdown("""
    <style>
    .stApp { background-color: #fcfcfc; }
    .stButton>button { 
        width: 100%; border-radius: 12px; 
        background: linear-gradient(90deg, #d50000, #0033a0);
        color: white; font-weight: bold; height: 3.5em; font-size: 18px;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #0033a0, #d50000);
        border: 2px solid #ffd700;
    }
    .thai-card { 
        background-color: white; padding: 18px; border-radius: 15px; 
        border-left: 8px solid #d93025; box-shadow: 0 4px 12px rgba(0,0,0,0.08); 
        margin-bottom: 20px; color: #1a1a1a;
    }
    .thai-word { font-size: 30px; font-weight: bold; color: #1a1a1a; }
    .thai-mean { font-size: 22px; font-weight: bold; color: #d93025; }
    .section-header { font-size: 1.2rem; font-weight: bold; color: #d93025; margin-bottom: 10px; border-bottom: 1px solid #eee; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. API設定 ---
api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("APIキーを設定してください。")
    st.stop()

# --- 3. メイン画面（画像とヘッダー） ---
col1, col2, col3 = st.columns([1,2,1])
with col2:
    if os.path.exists("musenseinew.jpg"):
        st.image("musenseinew.jpg", width=400)
    else:
        st.image("https://img.icons8.com/color/96/000000/thailand-circular.png", width=100)

st.markdown("<div style='text-align:center;'><h1>ムー先生の深掘りタイ語辞書 🐷🎓</h1></div>", unsafe_allow_html=True)

search_query = st.text_input("", placeholder="例：眠い / ง่วงนอน")

# --- 4. 生成ロジック ---
if st.button("ムー先生に教えてもらう！", use_container_width=True):
    if not search_query:
        st.warning("言葉を入力してくださいね！")
    else:
        with st.spinner('ムー先生が深掘り中...'):
            try:
                # 動作実績のあるモデル判別
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                target_models = ["models/gemini-1.5-flash", "models/gemini-1.5-pro", "models/gemini-pro"]
                model_name = next((m for m in target_models if m in available_models), available_models[0])
                model = genai.GenerativeModel(model_name=model_name)

                # プロンプトを一度変数に入れてから渡す（エラー回避のため）
                p_text = f"あなたはタイ語講師のムー先生です。{search_query}について、基本（タイ語|カタカナ|意味）、成り立ち、バリエーションの3点を解説してください。挨拶は不要です。"

                response = model.generate_content(p_text)
                full_text = response.text

                # シンプルな分割ロジック
                # AIの回答を「改行」で分けて、キーワードが含まれる行を探す
                lines = full_text.split('\n')
                
                # --- 表示 ---
                st.markdown('<div class="section-header">🔍 検索結果</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="thai-card">{full_text}</div>', unsafe_allow_html=True)
                
                # 音声（最初の1行目にタイ語がある前提で抽出）
                try:
                    thai_text = re.findall(r'[ก-๙]+', full_text)[0]
                    tts = gTTS(text=thai_text, lang="th")
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                        tts.save(fp.name)
                        st.audio(fp.name)
                except:
                    pass

            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

st.divider()
st.markdown("<div style='text-align: center; color: gray;'>Presented by Mr.Mu</div>", unsafe_allow_html=True)
