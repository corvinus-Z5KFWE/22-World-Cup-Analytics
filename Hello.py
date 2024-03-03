#Streamlit page creator
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import pandas as pd
from statsbombpy import sb
from mplsoccer import Pitch

st.set_page_config(page_title = "2022 World Cup - Interactive Player Analysis", page_icon = ":soccer:" , layout = "wide")

st.title(" :soccer:2022 World Cup - Interactive Player Analysis")
st.markdown('Created by: Z5KFWE - Gyetvai Marcell')
st.markdown('Navigate to other pages in order to get player statistics & visualizations.')
st.markdown('Overview - Passing Map & Shot Map & Heatmap')
st.markdown('Player profile - Compare a given player\'s performance to other players with a similiar position.')
st.markdown('Passing - detailed visualizations with context about every pass of a player in the given match.')
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html = True)
