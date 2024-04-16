#Streamlit page creator
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import pandas as pd
from statsbombpy import sb
from mplsoccer import Pitch,  VerticalPitch
import seaborn as sns
df = pd.read_csv('Full_World_Cup_data_pass_20240318.csv', sep = ',')
shotdf = pd.read_csv('Full_World_Cup_data_shot_20240318.csv', sep = '|')
defdf = pd.read_csv('Full_World_Cup_data_def_20240416.csv', sep = '|')

#Crate the sidebar for filtering
df['date'] = pd.to_datetime(df['match_date']).dt.date
#getting the min and max date of the start date 
startDate = df['date'].min()
endDate = df['date'].max()
col1, col2 = st.columns((2))
with col1: 
    date1 = (st.date_input("Start Date", startDate))

with col2: 
   date2 = (st.date_input("End Date", endDate))

df = df[(df['date'] >= date1) & (df['date'] <= date2)].copy()

# Create a match_ID
dataframes = [df, shotdf, defdf]
for dataframe in dataframes:
    dataframe['match_id'] = dataframe['competition_stage'] + '_' + dataframe['home_team'] + '_' + dataframe['away_team']


st.sidebar.header("Matches")
match_id = st.sidebar.multiselect("Pick your match:", df["match_id"].unique())
if match_id:
    df = df[df["match_id"].isin(match_id)]  # Apply match filter directly
    shotdf = shotdf[shotdf["match_id"].isin(match_id)]
    defdf = defdf[defdf["match_id"].isin(match_id)]

st.sidebar.header("Team")
pos_team = st.sidebar.multiselect("Filter down to the team with possession:", df["team"].unique())
if pos_team:
    df = df[df["team"].isin(pos_team)]  # Apply team filter directly
    shotdf = shotdf[shotdf["team"].isin(pos_team)]
    defdf = defdf[defdf["team"].isin(pos_team)]

st.sidebar.header("Player Position")
position = st.sidebar.multiselect("Filter down to players with a specific position:", df["position"].unique())
if position:
    df = df[df["position"].isin(position)]
    shotdf = shotdf[shotdf["position"].isin(position)]  # Apply position filter directly
    defdf = defdf[defdf["position"].isin(position)]

st.sidebar.header("Player")
player = st.sidebar.multiselect("Filter down to the player in action:", df["player"].unique())
if player:
    df = df[df["player"].isin(player)]  # Apply player filter directly
    shotdf = shotdf[shotdf["player"].isin(player)]
    defdf = defdf[defdf["player"].isin(player)]

def create_pass_map(df):
    pitch = Pitch(pitch_type = 'statsbomb', line_color='black')
    fig, ax = pitch.draw(figsize = (15,12) )
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

    pitch.scatter(df[mask_goal].x_end, df[mask_goal].y_end, s=200,
                    marker='football', edgecolors='black', c='white', zorder=2,
                    label='Assist', ax=ax)
        
    pitch.scatter(df[mask_shot].x_end, df[mask_shot].y_end, s=200,
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
    ax.legend( edgecolor='None', fontsize= 12 , loc='upper left', handlelength= 2)
    # Custom legend for statistics
    custom_legend_text = f'Total Passes: {total_passes}\nCompleted Passes: {completed_passes}\nMissed Passes: {uncompleted_passes}\nSuccess Rate: {success_rate:.2f}%\nAverage Pass Length: {average_pass_length}\nAverage Completed Pass Length: {average_length_for_completed_passes}\nAverage Missed Pass Length: {average_length_for_uncompleted_passes}'

# Adjust the x and y values according to your plot's layout
    ax.text(1, 0.95, custom_legend_text, transform=ax.transAxes, fontsize=12, verticalalignment='top')
    ax.set_title(f'All of {player}\'s passes & heatmap\n{match}', fontsize= 16)
    st.pyplot(fig)

def create_shot_map(df):
    if len(df) < 1: 
        print('The player has taken no shots.')
    else:
        shotdf_goal = df[df.shot_outcome == 'Goal'].copy()
        ontarget = {'Saved',  'Saved to Post', 'Post', 'Saved Off Target'} #006A4E
        shotdf_on_target = df[df['shot_outcome'].isin(ontarget)].copy()
        offtarget = {'Off T'} 
        shotdf_off_target = df[df['shot_outcome'].isin(offtarget)].copy()
        blockwayrum = {'Blocked',  'Wayward'}
        shotdf_blocked = df[df['shot_outcome'].isin(blockwayrum)].copy()
        player = df['player'].iloc[0]
        total_shots = len(df)
        goals = len(shotdf_goal)
        xg = df.shot_statsbomb_xg.sum()
        targetlen = len(shotdf_on_target)
        offtargetlen = len(shotdf_off_target)
        blockedlen = len(shotdf_blocked)
        if len(df.match_id.unique()) > 1:
            match = 'All matches'
        else: 
            match = df['match_id'].iloc[0]

        pitch = VerticalPitch(line_color='black', half = True)

        fig, ax = pitch.draw(figsize=(10, 8))

        # plot goal shots with a football marker
        # 'edgecolors' sets the color of the pentagons and edges, 'c' sets the color of the hexagons
        sc2 = pitch.scatter(shotdf_goal.x_start, shotdf_goal.y_start,
                            # size varies between 100 and 1900 (points squared)
                            s=(shotdf_goal.shot_statsbomb_xg * 1900) + 200,
                            edgecolors='black',
                            linewidths=0.3,
                            c='white',
                            marker='football',
                            label='Goal',
                            ax=ax)

        # plot on-target shots with hatch
        pitch.scatter(shotdf_on_target.x_start, shotdf_on_target.y_start,
                            # size varies between 100 and 1900 (points squared)
                            s=(shotdf_on_target.shot_statsbomb_xg * 1900) + 200,
                            edgecolors='#006A4E',  # give the markers a charcoal border
                            c='None',  # no facecolor for the markers
                            hatch='///',  # the all important hatch (triple diagonal lines)
                            marker='o',
                            label='On-target',
                            ax=ax)
        
        #shots off taerget
        pitch.scatter(shotdf_off_target.x_start, shotdf_off_target.y_start,
                            # size varies between 100 and 1900 (points squared)
                            s=(shotdf_off_target.shot_statsbomb_xg * 1900) + 200,
                            edgecolors='#b94b75',  # give the markers a charcoal border
                            c='None',  # no facecolor for the markers
                            hatch='///',  
                            marker='o',
                            label='Off target',
                            ax=ax)
        
        #Blocked/Wayrum shots
        pitch.scatter(shotdf_blocked.x_start, shotdf_blocked.y_start,
                            # size varies between 100 and 1900 (points squared)
                            s=(shotdf_blocked.shot_statsbomb_xg * 1900) + 200,
                            edgecolors='grey',  # give the markers a charcoal border
                            c='grey',  # no facecolor for the markers
                            marker='o',
                            label='Blocked/Other',
                            ax=ax)

        ax.legend( edgecolor='None', fontsize= 12 ,handlelength= 2.5, loc='upper left',  columnspacing=1.5, borderpad=2.5 )

        custom_legend_text = f'Bigger ball size -> Bigger xG\nTotal goals: {goals}\nExpected goals: {xg:.2f}\nTotal Shots: {total_shots}\nShots on target: {targetlen}\nShots off target: {offtargetlen}\nShots blocked/ Other: {blockedlen}'
        ax.text(1, 0.95, custom_legend_text, transform=ax.transAxes, fontsize=12, verticalalignment='top')
        #ax.legend(edgecolor='None', fontsize=12, loc='upper left', handlelength=2.5, bbox_to_anchor=(1, 1),ncol=1, columnspacing=0.5, borderpad=0.5)
        ax.set_title(f'All of {player}\'s shots \n{match}', fontsize= 16)
        st.pyplot(fig)

def create_defensive_actions_map(df):
    if len(df) < 1: 
        st.markdown('It seems like this player has not contributed defensively.')
    else:
        #Create specific df-s for plottinh
        df_recovery = df[df.type == 'Ball Recovery'].copy()
        df_duel = df[(df.type == 'Duel') | (df.type == '50/50') | (df.type == 'Shield')].copy()
        df_clear = df[df.type == 'Clearance'].copy()
        df_block = df[df.type == 'Block'].copy()
        df_intercept = df[df.type == 'Interception'].copy()

        #Check if only one match will be displayed or more
        if len(df.match_date.unique()) > 1:
                match = 'All matches'
        else: 
                match = df['match_id'].iloc[0]

        #Count the palyers actions
        total_defensive_actions = len(df)
        Recoveries = len(df_recovery)
        Duels = len(df_duel)
        Clearances = len(df_clear)
        Blocks = len(df_block)
        Interceptions = len(df_intercept)

        #Create the pitch and the heatmap
        pitch = VerticalPitch(line_color='#000009', line_zorder=2, pitch_color='white')
        fig, ax = pitch.draw(figsize=(10,8)) #4.4, 6.4, 
        player = df['player'].iloc[0]
        hexmap = pitch.hexbin(df.x_start, df.y_start, ax=ax, edgecolors='#f4f4f4',
                            gridsize=(8, 8), cmap= 'rocket_r')

        #Make the plots
        pitch.scatter(df_recovery.x_start, df_recovery.y_start, alpha = 1, s = 60, color = "red",  ax=ax,edgecolors="black", label = 'Recoveries') #ax=ax['pitch'],
        pitch.scatter(df_duel.x_start, df_duel.y_start, alpha = 1, s = 60, color = "purple",  ax=ax,edgecolors="black", label = 'Duels')
        pitch.scatter(df_clear.x_start, df_clear.y_start, alpha = 1, s = 60, color = "blue",  ax=ax,edgecolors="black", label = 'Clearances')
        pitch.scatter(df_block.x_start, df_block.y_start, alpha = 1, s = 60, color = "green",  ax=ax,edgecolors="black", label = 'Blocks')
        pitch.scatter(df_intercept.x_start, df_intercept.y_start, alpha = 1, s = 60, color = "grey",  ax=ax,edgecolors="black", label = 'Interceptions')

        #Legends and the counts of actions
        ax.legend( edgecolor='None', fontsize= 9 , loc='upper left', handlelength= 1)
        custom_legend_text = f'Total Defensive actions: {total_defensive_actions}\nRecoveries: {Recoveries}\nDuels: {Duels}\nClearances: {Clearances}\nBlocks: {Blocks}\nInterceptions: {Interceptions}'

        # Adjust the x and y values according to your plot's layout
        ax.text(1, 0.95, custom_legend_text, transform=ax.transAxes, fontsize=9, verticalalignment='top')
        ax.set_title(f'All of {player}\'s defensive actions & heatmap\n{match}', fontsize= 12)
        st.pyplot(fig)

if player:
        create_pass_map(df)
        create_defensive_actions_map(defdf)
        create_shot_map(shotdf)
        
else: 
    st.write("No data available for the selected filters.")
    