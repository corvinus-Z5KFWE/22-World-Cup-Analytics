#Streamlit page creator
import streamlit as st
import pandas as pd
from mplsoccer import PyPizza
import matplotlib.pyplot as plt


df = pd.read_csv('player_stats_merged_with_full_names2.csv', sep = ';')

params = [
    "goals", "npxg", "xg_net", "pass_xa", "sca",
    "touches_att_pen_area", "progressive_passes", "progressive_passes_received",
    "dribbles_completed", "touches_live_ball", "tackles_won", "aerials_won_pct"
]

gkparams_keys = [
    "gk_save_pct", "gk_pens_save_pct", "gk_psxg","gk_psxg_net_per90",
    "gk_passes_launched","gk_passes_pct_launched", "gk_passes", "gk_passes_length_avg",
    "gk_goal_kick_length_avg", "gk_crosses_stopped_pct", "gk_avg_distance_def_actions","gk_def_actions_outside_pen_area_per90"
]

defmidparam_key = [
    "tackles_interceptions", "clearances", "ball_recoveries","blocks",
    "dribbled_past","dribble_tackles", "dribbles_completed", "gca_per90",
    "passes_total_distance","passes_completed","progressive_passes", "passes_switches"
]


dpercentiles =  df[df["position"] == 'DF'][params].quantile(1)
dpercentiles2 =  df[df["position"] == 'DF'][defmidparam_key].quantile(1)

mpercentiles =  df[df["position"] == 'MF'][params].quantile(1)
mpercentiles2 =  df[df["position"] == 'MF'][defmidparam_key].quantile(1)

fpercentiles =  df[df["position"] == 'FW'][params].quantile(1)
fpercentiles2 =  df[df["position"] == 'FW'][defmidparam_key].quantile(1)

gkstats = df[df["position"] == 'GK'][gkparams_keys].quantile(1)

st.sidebar.header("Team")
pos_team = st.sidebar.multiselect("Filter down to a team:", df["team"].unique())
if pos_team:
    df = df[df["team"].isin(pos_team)]  # Apply team filter directly

st.sidebar.header("Player Position")
position = st.sidebar.multiselect("Filter down to players with a specific position:", df["position"].unique())
if position:
    df = df[df["position"].isin(position)]  # Apply position filter directly

player_position = df['position'].iloc[0]

def calculate_playervalues(percentiles):
    values = round((playervalues / percentiles * 100), 2).fillna(0)
    values = values.iloc[0].tolist()
    return values

def calculate_playerdefmidvalues(percentiles):
    defmidvalues = round((playerdefmidvalues / percentiles * 100), 2).fillna(0)
    defmidvalues = defmidvalues.iloc[0].tolist()
    return defmidvalues

values = ['0', '0','0','0','0','0','0','0','0','0','0','0']

st.sidebar.header("Player")
player = st.sidebar.multiselect("Filter down to the player in action:", df["player"].unique())
#Calculatinf the stats of the players that will be displayed on the pizza plot
# If the player is goalkeeper we only have to calculate the goalkeeping stats, if the player is not goalkeepers we are calculating the attacking stats together with defensive and playmaking attributes
if player:
    playerdf = df[df["player"].isin(player)]  #Loc the selected player
    playervalues = playerdf[params]
    playerdefmidvalues = playerdf[defmidparam_key]

    if playerdf['position'].iloc[0] == 'GK':
        playervalues = playerdf[gkparams_keys]
        values = calculate_playervalues(gkstats)
    elif playerdf['position'].iloc[0] == 'DF':
        values = calculate_playervalues(dpercentiles)
        defmidvalues = calculate_playerdefmidvalues(dpercentiles2)
    elif playerdf['position'].iloc[0] == 'MF':
        values = calculate_playervalues(mpercentiles)
        defmidvalues = calculate_playerdefmidvalues(mpercentiles2)
    else:
        values = calculate_playervalues(fpercentiles)
        defmidvalues = calculate_playerdefmidvalues(fpercentiles2)
else: 
    values = ['0', '0','0','0','0','0','0','0','0','0','0','0']

# Original parameter names and their more expressive counterparts
param_mapping = {
    "goals": "Goals",
    "npxg": "Non-Penalty\nExpected Goals",
    "xg_net": "Goals minus\nExpected Goals",
    "pass_xa": "Expected Assists",
    "sca": "Shot-Creating\nActions",
    "touches_att_pen_area": "Touches in\nattacking penalty area",
    "progressive_passes": "Progressive Passes",
    "progressive_passes_received": "Progressive Passes\nReceived",
    "dribbles_completed": "Dribbles Completed",
    "touches_live_ball": "Live-ball touches",
    "tackles_won": "Tackles won",
    "aerials_won_pct": "Percentage\nof aerials won"
}

gk_param_mapping = {
    "gk_save_pct": 'Save %',
    "gk_pens_save_pct": 'Penalty Save %', 
    "gk_psxg": 'Post-Shot\nExpected Goals', 
    "gk_psxg_net_per90":'Post-Shot Expected Goals\nminus Goals Allowed\nper 90 minutes', 
    "gk_passes_launched":'Passes longer than\n40 yards',
    "gk_passes_pct_launched":'Pass Completion %\nlonger than 40 yards',
    "gk_passes":'Passes Attempted', 
    "gk_passes_length_avg":'Average length\nof passes\nexlcuding goal kicks',
    "gk_goal_kick_length_avg":'Average length\nof goal kicks',
    "gk_crosses_stopped_pct":'% of\ncrosses stopeed', 
    "gk_avg_distance_def_actions":'Average distance\n of defensive actions', 
    "gk_def_actions_outside_pen_area_per90": 'Defence actions\nper 90 minutes'
}

defmid_param_mapping = {
    "tackles_interceptions": 'Tackles and interceptions',
    "clearances": 'Clearances',
    'ball_recoveries': 'Recoveries',
    "blocks": 'Blocks',
    'dribbled_past': 'Player dribbled\nPast',
    'dribble_tackles': 'Number of\n dribblers stopped',
    'dribbles_completed': 'Dribbles completed',
    'gca_per90': 'Goal creating actions\n per 90 minutes',
    'passes_total_distance': 'Total distance\n of passes',
    'passes_completed': 'Passes completed',
    'progressive_passes': 'Progressive passes',
    'passes_switches' : 'Switch passes\n of the field'
}

# Transform the parameter names using the mapping
attack_params = [param_mapping[param] for param in params]
gkparameters = [gk_param_mapping[param] for param in gkparams_keys]
defmid_params = [defmid_param_mapping[param] for param in defmidparam_key]

attactype = 'attacking'
keepertype = 'goalkeeping'
defmidtype = 'defensive & playmaking'

def create_pizza_plot(params,values,statstype):
# instantiate PyPizza class
    baker = PyPizza(
        params = params, #fix
        straight_line_color="#F2F2F2",  # color for straight lines
        straight_line_lw=1,             # linewidth for straight lines
        last_circle_lw=0,               # linewidth of last circle
        other_circle_lw=0,              # linewidth for other circles
    )

    plotcolor = playerdf['team_color'].iloc[0]
    player = playerdf['player'].iloc[0]
    pos = playerdf['position'].iloc[0]
# plot pizza
    fig, ax = baker.make_pizza(
        values,                                      # list of values
        figsize=(8, 8),                              # adjust figsize according to your need
        color_blank_space=["#C5C5C5"]*len(params),   # use same color to fill blank space
        blank_alpha=0.6,                             # alpha for blank-space colors
        kwargs_slices=dict(
            facecolor= plotcolor, edgecolor="#F2F2F2",
            zorder=2, linewidth= 3
        ),                                           # values to be used when plotting slices
        kwargs_params=dict(
            color="#000000", fontsize=12,
            va="center"
        ),                                           # values to be used when adding parameter
        kwargs_values=dict(
            color="#000000", fontsize=10,zorder=100,
            bbox=dict(
                edgecolor="#000000", facecolor= "#C5C5C5",
                boxstyle="round,pad=0.4", lw= 1
            )
        )                                            # values to be used when adding parameter-values
    )
    # add title
    fig.text(
        0.515, 0.97, f"{player}'s {statstype} stats", size=18,
        ha="center", color="#000000"
    )
    # add subtitle
    fig.text(
        0.515, 0.942,
        f"Rank vs Other {pos}'s | 2022 World Cup",
        size=15,
        ha="center", color="#000000"
    )
    # add credits
    CREDIT_1 = "data: statsbomb viz fbref"
    fig.text(
        0.99, 0.005, f"{CREDIT_1}", size=9,
        color="#000000",
        ha="right"
    )
    st.pyplot(fig)
    plt.tight_layout()  


# Reset matplotlib style to default
plt.style.use('default')
#if match_id or pos_team or player:
if player:
    if playerdf['position'].iloc[0] == 'GK':
        create_pizza_plot(gkparameters,values,keepertype)
        #params = gkparameters
    else:
        create_pizza_plot(attack_params, values, attactype)
        create_pizza_plot(defmid_params, defmidvalues,defmidtype)
        #params=attack_params  
else: 
    st.write("No data available for the selected filters.")

