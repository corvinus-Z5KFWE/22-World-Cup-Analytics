import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from mplsoccer import Pitch
from statsbombpy import sb
from mplsoccer import Pitch
import threading

# Function to plot the pitch
def plot_pitch(ax):
    pitch = Pitch(pitch_type='statsbomb')
    pitch.draw(ax=ax)

# Function to plot scatter points
def plot_scatter_points(ax, passes_df):
    pitch = Pitch(pitch_type='statsbomb')
    pitch.scatter(x=passes_df['x_start'], y=passes_df['y_start'], ax=ax)

# Function to plot lines
def plot_lines(ax, passes_df, mask_complete, mask_goal):
    pitch = Pitch(pitch_type='statsbomb')
    pitch.lines(xstart=passes_df[mask_complete].x_start, ystart=passes_df[mask_complete].y_start,
                xend=passes_df[mask_complete].x_end, yend=passes_df[mask_complete].y_end,
                lw=6, transparent=True, comet=True, label='completed passes',
                color='green', ax=ax)

    pitch.lines(xstart=passes_df[~mask_complete].x_start, ystart=passes_df[~mask_complete].y_start,
                xend=passes_df[~mask_complete].x_end, yend=passes_df[~mask_complete].y_end,
                lw=6, transparent=True, comet=True, label='uncompleted passes',
                color='red', ax=ax)

# Function to plot passes with threading
def plot_passes_with_threads(ax, passes_df, mask_complete, mask_goal):
    threads = []

    # Create threads for each plotting step
    pitch_thread = threading.Thread(target=plot_pitch, args=(ax,))
    scatter_thread = threading.Thread(target=plot_scatter_points, args=(ax, passes_df,))
    lines_thread = threading.Thread(target=plot_lines, args=(ax, passes_df, mask_complete, mask_goal,))

    # Start all threads
    pitch_thread.start()
    scatter_thread.start()
    lines_thread.start()

    # Wait for all threads to finish
    pitch_thread.join()
    scatter_thread.join()
    lines_thread.join()

# Streamlit page creator
matches_df = sb.matches(competition_id=43, season_id=106)
match_id = 3869685
event_df = sb.events(match_id=match_id)
df_360 = pd.read_json(f'{match_id}.json')
df = pd.merge(left=event_df, right=df_360, left_on='id', right_on='event_uuid', how='left')
df = df[df['type'] == 'Pass']
df[['x_start', 'y_start']] = pd.DataFrame(df.location.tolist(), index=df.index)
df[['x_end', 'y_end']] = pd.DataFrame(df.pass_end_location.tolist(), index=df.index)
df = pd.merge(df, matches_df, on='match_id', how='left')

df['date'] = pd.to_datetime(df['match_date']).dt.date
startDate = df['date'].min()
endDate = df['date'].max()

col1, col2 = st.columns((2))
with col1:
    date1 = st.date_input("Start Date", startDate)
with col2:
    date2 = st.date_input("End Date", endDate)

df = df[(df['date'] >= date1) & (df['date'] <= date2)].copy()

df['match_id'] = df['competition_stage'] + '_' + df['home_team'] + '_' + df['away_team']

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

if player:
    num_passes = len(df)
    num_cols = 2
    num_rows = (num_passes + 1) // 2

    fig, axes = plt.subplots(num_rows, num_cols, figsize=(15, 4 * num_rows))
    axes = axes.flatten()  

    for i, pass_index in enumerate(range(num_passes)):
        ax = axes[i]
        passes_df = df.iloc[[pass_index]]
        mask_complete = passes_df['pass_outcome'].isnull()
        mask_goal = passes_df['pass_goal_assist'].notnull()
        plot_passes_with_threads(ax, passes_df, mask_complete, mask_goal)

        comp = df['match_id'].iloc[0]
        distance = passes_df['pass_length'].iloc[0]
        timestamp = passes_df['timestamp'].iloc[0]
        receiver = passes_df['pass_recipient'].iloc[0]
        height = passes_df['pass_height'].iloc[0]
        passtype = passes_df['pass_type'].iloc[0]
        technique = passes_df['pass_technique'].iloc[0]
        play_pattern = passes_df['play_pattern'].iloc[0]

        ax.set_title(f'{player}\'s {i+1}. pass in the {comp}', fontsize=11)

        ax.legend(edgecolor='None', fontsize=9, loc='upper left', handlelength=4)
        custom_legend_text = f'Pass type: {passtype}\nPass receiver: {receiver}\nPlay type: {play_pattern}\nTechnique: {technique}\nPass Length: {distance}\nPass height: {height}\nTime {timestamp}'
        ax.text(1, 0.95, custom_legend_text, transform=ax.transAxes, fontsize=11, verticalalignment='top')

    for j in range(i + 1, num_rows * num_cols):
        fig.delaxes(axes[j])

    plt.tight_layout()
    st.pyplot(fig)
else:
    st.write("No data available for the selected filters.")
