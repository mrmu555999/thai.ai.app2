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
# RenderのEnvironment Variablesを優先して読み込む
api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("APIキーが設定されていません。")
    st.stop()

# --- 3. ヘッダー ---
st.markdown('<p class="main-title">ムー先生の深掘りタイ語辞書 🐷🎓</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">日本語からタイ語を、タイ文字から意味と成り立ちを調べよう！</p>', unsafe_allow_html=True)

# --- 4. 入力エリア ---
search_query = st.text_input("", placeholder="例：眠い / ง่วงนอน")

if search_query:
    with st.spinner('ムー先生が調べています...'):
        try:
            # 13:43時点で動いていた「1.5-flash」モデルを使用
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            prompt = f"""
            あなたはタイ語講師「ムー先生」です。【{search_query}】について解説してください。

            1. 【基本】: タイ語 | カタカナ読み | 日本語の意味
            2. 【成り立ち】: 単語を最小単位に分解して説明。
            3. 【バリエーション】: 日常フレーズを2〜3個。
            """

            response = model.generate_content(prompt)
            result_text = response.text

            # 表示ロジック
            sections = result_text.split('\n\n')

            # 🔍 検索結果
            st.markdown('<div class="dict-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="section-header">🔍 検索結果</div>', unsafe_allow_html=True)
            first_line = sections[0]
            st.write(first_line)
            
            # 音声再生（タイ文字を抽出）
            try:
                thai_text = first_line.split('|')[0].replace('【基本】:', '').strip()
                tts = gTTS(text=thai_text, lang="th")
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                    tts.save(fp.name)
                    st.audio(fp.name)
            except:
                pass
            st.markdown('</div>', unsafe_allow_html=True)

            # 🧩 成り立ちと 🚀 バリエーション
            for sec in sections[1:]:
                if "【成り立ち】" in sec:
                    st.markdown('<div class="dict-card">', unsafe_allow_html=True)
                    st.markdown(f'<div class="section-header">🧩 言葉の成り立ち</div>', unsafe_allow_html=True)
                    st.write(sec.replace('【成り立ち】:', ''))
                    st.markdown('</div>', unsafe_allow_html=True)
                elif "【バリエーション】" in sec:
                    st.markdown('<div class="dict-card">', unsafe_allow_html=True)
                    st.markdown(f'<div class="section-header">🚀 すぐに使える表現</div>', unsafe_allow_html=True)
                    st.write(sec.replace('【バリエーション】:', ''))
                    st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

# --- 5. 使い方ガイド ---
with st.sidebar:
    st.info("調べたい言葉を入力してね！")
