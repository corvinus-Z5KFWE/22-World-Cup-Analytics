#Streamlit page creator
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import pandas as pd
from statsbombpy import sb
from mplsoccer import Pitch
import matplotlib.pyplot as plt
import json

#df = pd.read_csv('statsbomb365_final_passes_final.csv', sep = '|')
matches_df = sb.matches(competition_id = 43, season_id = 106)
#WorldCup Final is the match_id 3869685 
match_id = 3869685
#Use statsbomb API to get data regarding the WC final
event_df = sb.events(match_id = match_id)
df_360 = pd.read_json(f'Football-projects/360_data/three-sixty/{match_id}.json')
df = pd.merge(left = event_df, right = df_360, left_on = 'id', right_on = 'event_uuid' , how = 'left')
df = df[df['type'] == 'Pass']
df[['x_start', 'y_start']] = pd.DataFrame(df.location.tolist(), index = df.index)
df[['x_end', 'y_end']] = pd.DataFrame(df.pass_end_location.tolist(), index = df.index)
df = pd.merge(df, matches_df, on='match_id', how='left')
#df = pd.read_csv('Full_World_Cup_data.csv', sep = '|')

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

filtered_df = df  # This is now your final filtered DataFrame

#if match_id or pos_team or player:
if player:
    # Determine the number of rows and columns for the subplot grid
    num_passes = len(df)
    num_cols = 2
    num_rows = (num_passes + 1) // 2  # Adding 1 to handle odd number of passes
    player = df['player'].unique()

    # Ábra létrehozása részábrákkal
    fig, axes = plt.subplots(num_rows, num_cols, figsize=(15, 4 * num_rows))  # Adjust the size as needed
    axes = axes.flatten()  # Flatten the axes array for easy iteration

    for i, pass_index in enumerate(range(num_passes)):
        ax = axes[i]
        pitch = Pitch(pitch_type='statsbomb')
        pitch.draw(ax=ax)  

        passes_df = df.iloc[[pass_index]]
        mask_complete = passes_df['pass_outcome'].isnull()
        mask_goal = passes_df['pass_goal_assist'].notnull()
        mask_shot = passes_df['pass_shot_assist'].notnull()
        comp = df['match_id'].iloc[0] 

        distance = passes_df['pass_length'].iloc[0] 
        timestamp = passes_df['timestamp'].iloc[0] 
        receiver = passes_df['pass_recipient'].iloc[0] 
        height = passes_df['pass_height'].iloc[0] 
        passtype = passes_df['pass_type'].iloc[0] 
        technique = passes_df['pass_technique'].iloc[0] 
        play_pattern = passes_df['play_pattern'].iloc[0] 
        

        pitch.scatter(x=passes_df['x_start'], y=passes_df['y_start'], ax=ax)

        #ax.set_title(f'{player}\'s {i+1}. pass in the World Cup Final \n distance = {distance} meters, type of pass = {passtype} \n time = {timestamp}, pass receiver = {receiver}', fontsize=10)
        ax.set_title(f'{player}\'s {i+1}. pass in the {comp}', fontsize=11)

        pitch.lines(xstart=passes_df[mask_complete].x_start, ystart=passes_df[mask_complete].y_start,
                    xend=passes_df[mask_complete].x_end, yend=passes_df[mask_complete].y_end,
                    lw=6, transparent=True, comet=True, label='completed passes',
                    color='green', ax=ax)

        pitch.lines(xstart=passes_df[~mask_complete].x_start, ystart=passes_df[~mask_complete].y_start,
                    xend=passes_df[~mask_complete].x_end, yend=passes_df[~mask_complete].y_end,
                    lw=6, transparent=True, comet=True, label='uncompleted passes',
                    color='red', ax=ax)
        
        pitch.scatter(passes_df[mask_goal].x_end, passes_df[mask_goal].y_end, s=90,
                    marker='football', edgecolors='black', c='white', zorder=2,
                    label='Assist', ax=ax)
        
        pitch.scatter(passes_df[mask_shot].x_end, passes_df[mask_shot].y_end, s=90,
                    edgecolors='white', c='#22312b', zorder=2,
                    label='Shot', ax=ax)

        freeze_frame = passes_df.iloc[0]['freeze_frame']
        #print(freeze_frame)
        #freeze_frame = json.loads(passes_df.iloc[0]['freeze_frame']) ##Meghatározása, hog ki volt csapattárs és ki ellenfél. 
        if isinstance(freeze_frame, list):
            for x in freeze_frame:
                #print(freeze_frame)
                if x['teammate']:
                    color = '#6CACE4'
                else:
                    color = '#ED2939'
                pitch.scatter(x=x['location'][0], y=x['location'][1], c=color, ax=ax, s=90)

        ax.legend(edgecolor='None', fontsize= 9, loc='upper left', handlelength=4)
        custom_legend_text = f'Pass type: {passtype}\nPass receiver: {receiver}\nPlay type: {play_pattern}\nTechnique: {technique}\nPass Length: {distance}\nPass height: {height}\nTime {timestamp}'
        # Adjust the x and y values according to your plot's layout
        ax.text(1, 0.95, custom_legend_text, transform=ax.transAxes, fontsize=11, verticalalignment='top')

    # Nem használt részábrák elrejtése
    for j in range(i + 1, num_rows * num_cols):
        fig.delaxes(axes[j])

    plt.tight_layout()     
    st.pyplot(fig)
else: 
    st.write("No data available for the selected filters.")

