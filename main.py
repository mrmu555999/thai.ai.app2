import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import tempfile
import os
import re

# --- 1. ページ設定 ---
st.set_page_config(page_title="ムー先生のタイ語‼️", page_icon="🇹🇭", layout="centered")

# スタイル設定
st.markdown("""
    <style>
    .stApp { background-color: #fcfcfc; }
    .stButton>button { 
        width: 100%; border-radius: 12px; 
        background: linear-gradient(90deg, #d50000, #0033a0);
        color: white; font-weight: bold; height: 3.5em; font-size: 18px;
    }
    .thai-card { 
        background-color: white; padding: 18px; border-radius: 15px; 
        border-left: 8px solid #d93025; box-shadow: 0 4px 12px rgba(0,0,0,0.08); 
        margin-bottom: 20px; color: #1a1a1a;
    }
    .thai-word { font-size: 30px; font-weight: bold; color: #1a1a1a; }
    .thai-mean { font-size: 20px; font-weight: bold; color: #d93025; }
    .section-header { font-size: 1.2rem; font-weight: bold; color: #d93025; margin-bottom: 10px; border-bottom: 1px solid #eee; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. API設定 ---
api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("APIキーの設定を確認してください。")
    st.stop()

# --- 3. メイン画面 ---
col1, col2, col3 = st.columns([1,2,1])
with col2:
    if os.path.exists("musenseinew.jpg"):
        st.image("musenseinew.jpg", width=400)
    else:
        st.image("https://img.icons8.com/color/96/000000/thailand-circular.png", width=100)

st.markdown("<div style='text-align:center;'><h1>ムー先生の深掘りタイ語辞書 🐷🎓</h1></div>", unsafe_allow_html=True)

search_query = st.text_input("", placeholder="例：眠い / ง่วงนอน")

# --- 4. 生成ロジック ---
if st.button("ムー先生に教えてもらう！"):
    if not search_query:
        st.warning("言葉を入力してくださいね！")
    else:
        with st.spinner('ムー先生が深掘り中...'):
            try:
                # モデルの自動判別
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                target_models = ["models/gemini-1.5-flash", "models/gemini-1.5-pro", "models/gemini-pro"]
                model_name = next((m for m in target_models if m in available_models), available_models[0])
                model = genai.GenerativeModel(model_name=model_name)

                # プロンプト（指示文を文字列として正しく設定）
                prompt = f"""
あなたはタイ語・タイ文化に精通した熱血講師「ムー先生」です。
キーワード【{search_query}】について解説してください。

【基本】
タイ語 | カタカナ | 日本語の意味

【成り立ち】
単語を分解した意味や由来の解説。

【バリエーション】
日常で使える例文を2つ。
"""

                response = model.generate_content(prompt)
                full_text = response.text

                # 「【項目名】」を基準に分割する正規表現
                sections = re.split(r'【.*?】', full_text)
                content_list = [s.strip() for s in sections if s.strip()]

                # 1. 検索結果（基本）
                if len(content_list) >= 1:
                    kihon = content_list[0]
                    parts = kihon.split('|')
                    thai = parts[0].strip() if len(parts) > 0 else kihon
                    kana = parts[1].strip() if len(parts) > 1 else ""
                    imi  = parts[2].strip() if len(parts) > 2 else ""

                    st.markdown('<div class="section-header">🔍 検索結果</div>', unsafe_allow_html=True)
                    st.markdown(f'''
                        <div class="thai-card">
                            <div class="thai-word">{thai}</div>
                            <div style="color: #666;">{kana}</div>
                            <div class="thai-mean">👉 {imi}</div>
                        </div>
                    ''', unsafe_allow_html=True)
                    
                    try:
                        tts = gTTS(text=thai, lang="th")
                        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                        tts.save(tmp.name)
                        st.audio(tmp.name)
                    except: pass

                # 2. 成り立ち
                if len(content_list) >= 2:
                    st.markdown('<div class="section-header">🧩 言葉の成り立ち</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="thai-card">{content_list[1]}</div>', unsafe_allow_html=True)

                # 3. バリエーション
                if len(content_list) >= 3:
                    st.markdown('<div class="section-header">🚀 すぐに使える表現</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="thai-card">{content_list[2]}</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"エラーが発生しましたクラップ: {e}")

st.divider()
st.markdown("<div style='text-align: center; color: gray;'>Presented by Mr.Mu</div>", unsafe_allow_html=True)
