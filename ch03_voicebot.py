import streamlit as st
import openai
from audiorecorder import audiorecorder
import os
from datetime import datetime
import numpy as np
from gtts import gTTS
import base64

def STT(audio):
    filename = "input.mp3"
    wav_file = open(filename, "wb")
    wav_file.write(audio.tobytes())
    wav_file.close()
    
    audio_file = open(filename, "rb")
    transcript= openai.Audio.transcribe("whisper-1", audio_file)
    audio_file.close()
    os.remove(filename)
    return transcript["text"]

def ask_gpt(prompt, model):
    response = openai.ChatCompletion.create(model=model, message = prompt)
    system_message = response["choices"][0]["message"]
    return system_message["content"]

def TTS(response):
    filename = "output.mp3"
    tts = gTTS(text=response, lang="ko")
    tts.save(filename)

    with open(filename, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay = "True">
            <source src = "data:audio/mp3;base64, {b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True,)
    os.remove(filename)

def main():

    st.set_page_config(
        page_title="NIA 음성 비서 프로그램",
        layout="wide")
    
    flag_start = False
    
    st.header("NIA 음성 비서 프로그램")

    st.markdown("-----")

    with st.expander("음성비서 프로그램에 관하여", expanded=True):
        st.write(
            """
            - 음성비서 프로그램의 UI는 스트림릿을 활용했습니다.
            - STT(Speech-To-Text)는 OpenAI의 Whisper AI를 활용했습니다.
            - 답변은 OpenAI의 GPT 모델을 활용했습니다.
            - TTS(Text-to-Speech)는 구글의 Google Translate TTS를 활용했습니다.
            """
        )
        st.markdown("")

    if "chat" not in st.session_state:
        st.session_state["chat"] = []

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "system", "content":"You are a thoughtful assisstant. Respond to all answer in korea"}]

    if "check_audio" not in st.session_state:
        st.session_state["check_audio"] = []

    with st.sidebar:

        openai.api_key = st.text_input(label = "OPENAI API 키", placeholder="Enter Your API Key", value="", type="password")

        st.markdown("---")

        model = st.radio(label="GPT 모델", options=["gpt-4", "gpt-3.5-turbo"])

        st.markdown("---")

        if st.button(label="초기화"):
            st.session_state["chat"]=[]
            st.session_state["messages"]= [{"role": "system", "content":"You are a thoughtful assisstant. Respond to all answer in korea"}]


    col1, col2 = st.columns(2)

    with col1:
        st.subheader("질문하기")

        audio = audiorecorder("클릭하여 녹음하기", "녹음 중...")

        if len(audio) > 0 and not np.array_equal(audio, st.session_state["check_audio"]):
            st.audio(audio.tobytes())
            question = STT(audio)
            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"] = st.session_state["chat"] + [("user", now, question)]
            st.session_state["messages"] = st.session_state["messages"] + [{"role":"user", "content": question}]
            st.session_state["check_audio"] = audio
            flag_start = True


    with col2:
        st.subheader("질문/답변")
        if flag_start:
            response = ask_gpt(st.session_state["messages", model])
            st.session_state["messages"] = st.session_state["messages"] + [{"role":"system", "content":response}]
            now =datetime.now().strftime("%H:%M")
            st.session_state["chat"] = st.session_state["chat"] + [("bot", now, response)]

            for sender, time, message in st.session_state["chat"]:
                if sender == "user":
                    st.write(f'<div style = "display:flex;align-items:center;"><div style = "background-color:#007AFF;color:white;border-radius:12px;padding:8px 12px;margin-right:8pxl"</div><div style = "fond-size:0.8rem;color:gray;">{time}</div>', unsafe_allow_html=True)
                    st.write("")
                else:
                    st.write(f'<div style="display:flex;align=items:center;justify=content:flex-end;"><div style="background-color:lightgray;border-radius:12px;padding:8px 12px;margin-left:8px;">{message}</div><div style="font-size:0.8rem;color:gray;">{time}</div></div>', unsafe_allow_html=True)
                    st.write("")

            TTS(response)

if __name__=="__main__":
    main()



