import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import tempfile
import os
import re

# --- 1. ページ設定（初代のデザインを継承） ---
st.set_page_config(
    page_title="ムー先生のタイ語‼️",
    page_icon="🇹🇭",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 背景色とスタイルの設定（初代Mr.Muカスタムスタイルを完全再現）
st.markdown("""
    <style>
    .stApp { background-color: #fcfcfc; }
    .stButton>button { 
        width: 100%; 
        border-radius: 12px; 
        background: linear-gradient(90deg, #d50000, #0033a0);
        color: white; 
        font-weight: bold; 
        border: 2px solid #ffffff;
        height: 3.5em;
        font-size: 18px;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #0033a0, #d50000);
        border: 2px solid #ffd700;
    }
    .thai-card { 
        background-color: white; 
        padding: 18px; 
        border-radius: 15px; 
        border-left: 8px solid #d93025; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.08); 
        margin-bottom: 20px; 
        color: #1a1a1a;
    }
    .thai-word { font-size: 30px; font-weight: bold; color: #1a1a1a; margin-bottom: 5px; }
    .thai-mean { font-size: 20px; font-weight: bold; color: #d93025; margin-top: 5px; }
    .section-header { font-size: 1.2rem; font-weight: bold; color: #d93025; margin-bottom: 10px; border-bottom: 1px solid #eee; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. セキュリティ・モデル設定 ---
api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("APIキーの設定を確認してください。")
    st.stop()

# --- 3. メイン画面（画像とヘッダーの完全再現） ---

col1, col2, col3 = st.columns([1,2,1])
with col2:
    try:
        st.image("musenseinew.jpg", width=400)
    except:
        st.warning("画像 'musenseinew.jpg' を読み込めません。")

st.markdown("""
<div style='text-align:center;'>
<h1 style="margin-bottom:0;">
ムー先生<span style="font-size:0.8em;">の</span>深掘りタイ語辞書 🐷🎓
</h1>
<div style='font-size:1.1rem; font-weight:bold; margin-top:20px; margin-bottom:20px;'>
日本語からタイ語を、タイ文字から成り立ちを調べよう！✏️<br>
単語を分解して理解すれば、語彙力がグンとアップします 🇹🇭💬
</div>
</div>
""", unsafe_allow_html=True)

# 入力エリア
search_query = st.text_input("", placeholder="例：眠い / ง่วงนอน")

# --- 4. 生成ロジック ---
if st.button("ムー先生に教えてもらう！", use_container_width=True):

    if not search_query:
        st.warning("調べたい言葉を入力してくださいね！")
    else:
        with st.spinner('ムー先生AIが深掘り解説を作成中...'):
            try:
                # 動いているコードの自動判別ロジック
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                target_models = ["models/gemini-1.5-flash", "models/gemini-1.5-pro", "models/gemini-pro"]
                model_name = next((m for m in target_models if m in available_models), available_models[0])
                model = genai.GenerativeModel(model_name=model_name)

                prompt = f"""
                タイ語講師「ムー先生」として【{search_query}】を深掘り解説してください。
                必ず以下の3項目を正確に含めてください。挨拶は不要です。

                【基本】: タイ語 | カタカナ読み | 日本語の意味
                【成り立ち】: 語源やパーツ分解の説明（例：A + B）
                【バリエーション】: その言葉を使った日常フレーズを2〜3個
                """

                response = model.generate_content(prompt)
                full_text = response.text

                # 抜き出し用関数
                def extract(label, text):
                    pattern = f"【{label}】:?(.*?)(?=\\n\\d|\\n【|$)"
                    match = re.search(pattern, text, re.DOTALL)
                    return match.group(1).strip() if match else ""

                kihon = extract("基本", full_text)
                naritachi = extract("成り立ち", full_text)
                variation = extract("バリエーション", full_text)

                # --- 抽出結果を初代のカード形式で表示 ---
                
                # 1. 基本
                if kihon:
                    st.markdown('<div class="section-header">🔍 検索結果</div>', unsafe_allow_html=True)
                    st.markdown(f'''
                    <div class="thai-card">
                        <div class="thai-word">{kihon.split('|')[0] if "|" in kihon else kihon}</div>
                        <div style="color: #666;">{kihon.split('|')[1] if kihon.count('|')>=2 else ""}</div>
                        <div class="thai-mean">&#128073; {kihon.split('|')[-1] if "|" in kihon else ""}</div>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    # 音声
                    try:
                        thai_for_tts = kihon.split('|')[0].strip()
                        tts = gTTS(text=thai_for_tts, lang="th")
                        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                        tts.save(tmp.name)
                        st.audio(tmp.name)
                    except: pass

                # 2. 成り立ち
                if naritachi:
                    st.markdown('<div class="section-header">🧩 言葉の成り立ち</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="thai-card">{naritachi}</div>', unsafe_allow_html=True)

                # 3. バリエーション
                if variation:
                    st.markdown('<div class="section-header">🚀 すぐに使える表現</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="thai-card">{variation}</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

# --- 5. フッター ---
st.divider()
st.markdown("<div style='text-align: center; color: gray;'>Presented by Mr.Mu</div>", unsafe_allow_html=True)
