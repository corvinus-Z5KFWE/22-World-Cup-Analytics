#Streamlit page creator
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import pandas as pd
from statsbombpy import sb
from mplsoccer import Pitch
import seaborn as sns
df = pd.read_csv('Full_World_Cup_data_finals.csv', sep = '|')

#Crate the sidebar for filtering
df['date'] = pd.to_datetime(df['match_date']).dt.date
##getting the min and max date of the start date 
startDate = df['date'].min()
endDate = df['date'].max()
col1, col2 = st.columns((2))
with col1: 
    date1 = (st.date_input("Start Date", startDate))

with col2: 
    date2 = (st.date_input("End Date", endDate))

df = df[(df['date'] >= date1) & (df['date'] <= date2)].copy()

# Create a match_ID
df['match_id'] = df['competition_stage'] + '_' + df['home_team'] + '_' + df['away_team']

st.sidebar.header("Matches")
match_id = st.sidebar.multiselect("Pick your match:", df["match_id"].unique())
if match_id:
    df = df[df["match_id"].isin(match_id)]  # Apply match filter directly

st.sidebar.header("Team")
pos_team = st.sidebar.multiselect("Filter down to the team with possession:", df["team"].unique())
if pos_team:
    df = df[df["team"].isin(pos_team)]  # Apply team filter directly

st.sidebar.header("Player Position")
position = st.sidebar.multiselect("Filter down to players with a specific position:", df["position"].unique())
if position:
    df = df[df["position"].isin(position)]  # Apply position filter directly

st.sidebar.header("Player")
player = st.sidebar.multiselect("Filter down to the player in action:", df["player"].unique())
if player:
    df = df[df["player"].isin(player)]  # Apply player filter directly

def create_pass_map(df): 
    pitch = Pitch(pitch_type = 'statsbomb')
    fig, ax = pitch.draw(figsize = (10,8) )
    mask_complete = df.pass_outcome.isnull()
    mask_goal = df.pass_goal_assist.astype('float').notnull()
    mask_shot = df.pass_shot_assist.astype('float').notnull()
    player = df['player'].iloc[0]
    if len(df.match_id.unique()) > 1:
        match = 'All matches'
    else: 
        match = df['match_id'].iloc[0]

    total_passes = len(df)
    completed_passes = len(df[mask_complete])
    uncompleted_passes = len(df[~mask_complete])
    success_rate = (completed_passes / total_passes) * 100
    average_length_for_completed_passes = round(df.pass_length[mask_complete].mean(),2)
    average_length_for_uncompleted_passes = round(df.pass_length[~mask_complete].mean(),2)
    average_pass_length = round(df.pass_length.mean(),2)

    pitch.scatter(x=df['x_start'], y=df['y_start'], ax=ax)

    #Plot the completed passed
    pitch.lines(xstart = df[mask_complete].x_start, ystart = df[mask_complete].y_start,
                    xend = df[mask_complete].x_end, yend = df[mask_complete].y_end,
                    lw=3, transparent=True, comet=True, label='completed passes',
                    color='green', ax=ax)

    pitch.lines(xstart = df[~mask_complete].x_start, ystart = df[~mask_complete].y_start,
                    xend = df[~mask_complete].x_end, yend = df[~mask_complete].y_end,
                    lw=3, transparent=True, comet=True, label='uncompleted passes',
                    color='red', ax=ax)

    pitch.scatter(df[mask_goal].x_end, df[mask_goal].y_end, s=100,
                    marker='football', edgecolors='black', c='white', zorder=2,
                    label='Assist', ax=ax)
        
    pitch.scatter(df[mask_shot].x_end, df[mask_shot].y_end, s=100,
                   edgecolors='white', c='#22312b', zorder=2,
                  label='Shot', ax=ax)
    
        #Create a heatmap
    kde = sns.kdeplot(
            x = df['x_start'],
            y = df['y_start'],
            shade_lowest = False,
            alpha = 0.2,
            shade = True,
            n_levels = 12,
            cmap = 'rocket_r' #viridis
    )
    plt.xlim(0,121)
    plt.ylim(0,80)

    # Plot the legend
    ax.legend( edgecolor='None', fontsize= 12 , loc='upper left', handlelength= 4)
    # Custom legend for statistics
    custom_legend_text = f'Total Passes: {total_passes}\nCompleted Passes: {completed_passes}\nMissed Passes: {uncompleted_passes}\nSuccess Rate: {success_rate:.2f}%\nAverage Pass Length: {average_pass_length}\nAverage Completed Pass Length: {average_length_for_completed_passes}\nAverage Missed Pass Length: {average_length_for_uncompleted_passes}'

# Adjust the x and y values according to your plot's layout
    ax.text(1, 0.95, custom_legend_text, transform=ax.transAxes, fontsize=10, verticalalignment='top')
    ax_title = ax.set_title(f'All of {player}\'s passes & heatmap\n{match}', fontsize= 14)
    st.pyplot(fig)


if player:
    create_pass_map(df)
else: 
    st.write("No data available for the selected filters.")
    