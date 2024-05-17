import streamlit as st
import pandas as pd

st.set_page_config(page_title="2022 World Cup - Interactive Player Analysis", page_icon=":soccer:", layout="wide")

st.title(":soccer: 2022 World Cup - Interactive Player Analysis")
st.markdown('Created by: Z5KFWE - Gyetvai Marcell')

st.markdown("""
    <style>
    .box {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 150px;
        margin: 20px 0;
        padding: 20px;
        border-radius: 15px;
        background-color: #f0f2f6;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s, background-color 0.2s;
        text-align: center;
    }
    .box:hover {
        transform: scale(1.05);
        background-color: #e0e2e8;
    }
    .box h2 {
        margin: 0;
        font-size: 24px;
        font-weight: bold;
    }
    .box p {
        margin: 10px 0 0;
        font-size: 16px;
    }
    a {
        text-decoration: none;
        color: inherit;
    }
    </style>
""", unsafe_allow_html=True)

# Boxes
boxes = [
    {"title": "Overview", "description": "Passing Map & Shot Map & Heatmap of the selected player's actions in the tournament/in the selected match.", "link": "https://22-world-cup-analytics.streamlit.app/Overview"},
    {"title": "Player Profile", "description": "Compare a given player's performance to other players operating in a similar position.", "link": "https://22-world-cup-analytics.streamlit.app/Player_profile"},
    {"title": "Passing", "description": "Detailed visualizations with context about every pass of a player in the selected match.", "link": "https://22-world-cup-analytics.streamlit.app/Passing"}
]

for box in boxes:
    st.markdown(f"""
        <a href="{box['link']}" target="_self">
            <div class="box">
                <h2>{box['title']}</h2>
                <p>{box['description']}</p>
            </div>
        </a>
    """, unsafe_allow_html=True)

# Adding a padding style
st.markdown('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)
