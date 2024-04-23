import streamlit as st
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import pandas as pd
from statsbombpy import sb

# Fetching match data
matches_df = sb.matches(competition_id=43, season_id=106)
match_id = 3869685
event_df = sb.events(match_id=match_id)
df_360 = pd.read_json(f'{match_id}.json')
df = pd.merge(left=event_df, right=df_360, left_on='id', right_on='event_uuid', how='left')
df = df[df['type'] == 'Pass']
df[['x_start', 'y_start']] = pd.DataFrame(df.location.tolist(), index=df.index)
df[['x_end', 'y_end']] = pd.DataFrame(df.pass_end_location.tolist(), index=df.index)
df = pd.merge(df, matches_df, on='match_id', how='left')

# Sidebar for filtering
df['date'] = pd.to_datetime(df['match_date']).dt.date
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

# Sidebar for filtering matches, teams, player positions, and players
st.sidebar.header("Matches")
match_id = st.sidebar.multiselect("Pick your match:", df["match_id"].unique())
if match_id:
    df = df[df["match_id"].isin(match_id)]  

st.sidebar.header("Team")
pos_team = st.sidebar.multiselect("Filter down to the team with possession:", df["team"].unique())
if pos_team:
    df = df[df["team"].isin(pos_team)]  

st.sidebar.header("Player Position")
position = st.sidebar.multiselect("Filter down to players with a specific position:", df["position"].unique())
if position:
    df = df[df["position"].isin(position)]  

st.sidebar.header("Player")
player = st.sidebar.multiselect("Filter down to the player in action:", df["player"].unique())
if player:
    df = df[df["player"].isin(player)]  

filtered_df = df  

# Plotting passes
if player:
    num_passes = len(df)
    num_cols = 2
    num_rows = (num_passes + 1) // 2
    player = df['player'].iloc[0] 

    for i, pass_index in enumerate(range(num_passes)):
        fig, ax = plt.subplots(figsize=(15, 8))
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
        ax.set_title(f'{player}\'s {i+1}. pass in the {comp}', fontsize=14)

        pitch.lines(xstart=passes_df[mask_complete].x_start, ystart=passes_df[mask_complete].y_start,
                    xend=passes_df[mask_complete].x_end, yend=passes_df[mask_complete].y_end,
                    lw=6, transparent=True, comet=True, label='completed passes',
                    color='green', ax=ax)

        pitch.lines(xstart=passes_df[~mask_complete].x_start, ystart=passes_df[~mask_complete].y_start,
                    xend=passes_df[~mask_complete].x_end, yend=passes_df[~mask_complete].y_end,
                    lw=6, transparent=True, comet=True, label='uncompleted passes',
                    color='red', ax=ax)
        
        pitch.scatter(passes_df[mask_goal].x_end, passes_df[mask_goal].y_end, s=100,
                    marker='football', edgecolors='black', c='white', zorder=2,
                    label='Assist', ax=ax)
        
        pitch.scatter(passes_df[mask_shot].x_end, passes_df[mask_shot].y_end, s=100,
                    edgecolors='white', c='#22312b', zorder=2,
                    label='Shot', ax=ax)

        freeze_frame = passes_df.iloc[0]['freeze_frame']
        if isinstance(freeze_frame, list):
            for x in freeze_frame:
                if x['teammate']:
                    color = '#6CACE4'
                else:
                    color = '#ED2939'
                pitch.scatter(x=x['location'][0], y=x['location'][1], c=color, ax=ax, s=100)

        ax.legend(edgecolor='None', fontsize= 12, loc='upper left', handlelength=4)
        custom_legend_text = f'Pass type: {passtype}\nPass receiver: {receiver}\nPlay type: {play_pattern}\nTechnique: {technique}\nPass Length: {distance}\nPass height: {height}\nTime {timestamp}'
        ax.text(1, 0.95, custom_legend_text, transform=ax.transAxes, fontsize=14, verticalalignment='top')

        st.pyplot(fig)
        plt.close(fig)  # Close the figure to avoid memory leaks

else: 
    st.write("No data available for the selected filters.")
