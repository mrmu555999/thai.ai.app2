import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import tempfile
import os
import re

# --- 1. ページ設定 ---
st.set_page_config(page_title="ムー先生のタイ語‼️", page_icon="🇹🇭", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #fcfcfc; }
    .stButton > button { 
        width: 100%; border-radius: 12px; 
        background: linear-gradient(90deg, #d50000, #0033a0);
        color: white; font-weight: bold; height: 3.5em; font-size: 18px;
        border: 2px solid #ffffff;
    }
    .stButton > button:hover { background: linear-gradient(90deg, #0033a0, #d50000); border: 2px solid #ffd700; }
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

# --- 3. メイン画面 ---
col1, col2, col3 = st.columns([1,2,1])
with col2:
    if os.path.exists("musenseinew.jpg"):
        st.image("musenseinew.jpg", width=400)
    else:
        st.image("https://img.icons8.com/color/96/000000/thailand-circular.png", width=100)

st.markdown("""
<div style='text-align:center; margin-top: 10px;'>
    <h1 style="font-size: 2rem; margin-bottom: 5px;">ムー先生の深掘りタイ語辞書 🐷🎓</h1>
    <p style='font-size: 0.95rem; font-weight: normal; color: #666; margin-bottom: 20px;'>
        日本語やタイ語（単語も文章もOK）を入力してね！
    </p>
</div>
""", unsafe_allow_html=True)

search_query = st.text_input("", placeholder="例：眠い / ง่วงนอน")

# --- 4. 生成ロジック ---
if st.button("ムー先生に教えてもらう！", use_container_width=True):
    if not search_query:
        st.warning("言葉を入力してくださいね！")
    else:
        with st.spinner('ムー先生AIが精力的に作成中...'):
            try:
                # モデル選定
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                target_models = ["models/gemini-1.5-flash", "models/gemini-1.5-pro", "models/gemini-pro"]
                model_name = next((m for m in target_models if m in available_models), available_models[0])
                model = genai.GenerativeModel(model_name=model_name)

                # 【超重要】お喋りを封じ、形式を強制するプロンプト
                p_text = f"""
【最優先指示】挨拶、前置き、自己紹介（サワッディーカップ等）は一切禁止です。
以下の3つのタグを使って、指定の形式のみ出力してください。

【①意味】
タイ語 | カタカナ | 日本語の意味

【②成り立ち】
言葉の分解や由来の簡潔な解説。

【③すぐに使える表現】
1. タイ語 | カタカナ | 意味
2. タイ語 | カタカナ | 意味
3. タイ語 | カタカナ | 意味

キーワード：{search_query}
"""

                response = model.generate_content(p_text)
                full_text = response.text

                # セクション分割ロジック
                parts = re.split(r'【.*?】', full_text)
                content = [p.strip() for p in parts if p.strip()]

                # --- 1. 意味 ---
                if len(content) >= 1:
                    base_info = content[0].split('|')
                    t_word = base_info[0].strip() if len(base_info) > 0 else content[0]
                    t_kana = base_info[1].strip() if len(base_info) > 1 else ""
                    t_imi  = base_info[2].strip() if len(base_info) > 2 else ""

                    st.markdown('<div class="section-header">🔍 ①意味</div>', unsafe_allow_html=True)
                    st.markdown(f'''<div class="thai-card"><div class="thai-word">{t_word}</div><div style="color: #666;">{t_kana}</div><div class="thai-mean">👉 {t_imi}</div></div>''', unsafe_allow_html=True)
                    
                    try:
                        tts = gTTS(text=t_word, lang="th")
                        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                        tts.save(tmp.name)
                        st.audio(tmp.name)
                    except: pass

                # --- 2. 成り立ち ---
                if len(content) >= 2:
                    st.markdown('<div class="section-header">🧩 ②言葉の成り立ち</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="thai-card">{content[1]}</div>', unsafe_allow_html=True)

                # --- 3. すぐに使える表現 ---
                if len(content) >= 3:
                    st.markdown('<div class="section-header">🚀 ③すぐに使える簡単な表現</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="thai-card">{content[2].replace("|", " | ")}</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"エラー: {e}")

st.divider()
st.markdown("<div style='text-align: center; color: gray;'>Presented by Mr.Mu</div>", unsafe_allow_html=True)
