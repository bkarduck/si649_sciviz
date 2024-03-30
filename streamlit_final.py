# load up the libraries
import panel as pn
import pandas as pd
import altair as alt
# from vega_datasets import data
import json
import numpy as np
import streamlit as st



# loading the events data
events={}
# nations = ['Italy','England','Germany','France','Spain','European_Championship','World_Cup']
# select only the European Championship
nations = ['European_Championship']
for nation in nations:
    with open('./data/events/events_%s.json' %nation) as json_data:
        events[nation] = json.load(json_data)
        
# loading the match data
matches={}
nations = ['European_Championship']
for nation in nations:
    with open('./data/matches/matches_%s.json' %nation) as json_data:
        matches[nation] = json.load(json_data)

teams={}
with open('./data/teams.json') as json_data:
    teams = json.load(json_data)


# Adjusted helper function to ensure lines are closed for areas
def draw_pitch_altair():
    # this was generated mostly with AI help, based off of the original function provided in the soccer nsd code file
    def create_closed_line_df(points):
        # Append the first point at the end to close the shape
        points.append(points[0])
        return pd.DataFrame(points, columns=['x', 'y']).reset_index()

    # Correctly defining the penalty and goal areas as closed shapes
    pitch_outline_df = create_closed_line_df([[0, 0], [104, 0], [104, 68], [0, 68], [0, 0]])
    penalty_area_left_df = create_closed_line_df([[0, 13.84], [16.5, 13.84], [16.5, 54.16], [0, 54.16]])
    penalty_area_right_df = create_closed_line_df([[104, 13.84], [87.5, 13.84], [87.5, 54.16], [104, 54.16]])
    goal_area_left_df = create_closed_line_df([[0, 24.84], [4.5, 24.84], [4.5, 43.16], [0, 43.16]])
    goal_area_right_df = create_closed_line_df([[104, 24.84], [99.5, 24.84], [99.5, 43.16], [104, 43.16]])
    # Halfway line, penalty spots, and kickoff spot
    halfway_line_df = create_closed_line_df([[52, 0], [52, 68]])
    penalty_spot_left_df = pd.DataFrame({'x': [11], 'y': [34]})
    penalty_spot_right_df = pd.DataFrame({'x': [93], 'y': [34]})
    kickoff_spot_df = pd.DataFrame({'x': [52], 'y': [34]})

    # Base chart for pitch outline
    base_chart = alt.Chart(pitch_outline_df).mark_line().encode(x='x', y='y', order='index')

    # Function to add elements to the chart
    def add_element(chart, df, element_type='line', size=30):
        if element_type == 'line':
            return chart + alt.Chart(df).mark_line().encode(x='x', y='y', order='index')
        elif element_type == 'point':
            return chart + alt.Chart(df).mark_point(size=size).encode(x='x', y='y')

    # Adding elements to the base chart with corrections for closed shapes
    final_chart = base_chart
    final_chart = add_element(final_chart, penalty_area_left_df)
    final_chart = add_element(final_chart, penalty_area_right_df)
    final_chart = add_element(final_chart, goal_area_left_df)
    final_chart = add_element(final_chart, goal_area_right_df)
    final_chart = add_element(final_chart, halfway_line_df)
    final_chart = add_element(final_chart, penalty_spot_left_df, 'point', 100)
    final_chart = add_element(final_chart, penalty_spot_right_df, 'point', 100)
    final_chart = add_element(final_chart, kickoff_spot_df, 'point', 100)

    # Setting the scale to better fit the soccer field dimensions
    final_chart = final_chart.properties(width=600, height=400).configure_view(strokeWidth=0)

    return final_chart

# get just the european championship matches and events
euro_matches = matches['European_Championship']
euro_events = events['European_Championship']
euro_match_df = pd.DataFrame(euro_matches)
euro_events_df = pd.DataFrame(euro_events)

# get all countries in the euro championship
all_countries = []
for i in range(len(euro_match_df)):
    all_countries.append(list(euro_match_df['teamsData'][i].keys())[0])
    all_countries.append(list(euro_match_df['teamsData'][i].keys())[1])

all_countries = list(set(all_countries))
all_country_names = []
all_country_ids = []

for team in teams:
    if str(team['wyId']) in all_countries and team['name'] not in all_country_names:
        all_country_ids.append(team['wyId'])
        all_country_names.append(team['name'])


team2_nameX=''
team1_nameX=''
for team in teams:
    if team['wyId'] == int(list(euro_match_df['teamsData'][0].keys())[0]):

        team1_nameX = team['name']
    if team['wyId'] == int(list(euro_match_df['teamsData'][0].keys())[1]):
        team2_nameX = team['name']
    if team1_nameX != "" and team2_nameX != "":
        break



def get_match_list(euro_matches):
    match_list = []
    for matchX in euro_matches:
        # Generate a unique descriptor for each match - adjust according to your data structure
        team1_name=''
        team2_name=''
        team2_id=list(matchX['teamsData'].keys())[1]
        team1_id=list(matchX['teamsData'].keys())[0]
        for team in teams:
            if team['wyId'] == int(team1_id):
                team1_name = team['name']
            if team['wyId'] == int(team2_id):
                team2_name = team['name']
          
        match_desc = f"{team1_name} vs {team2_name} on {matchX['dateutc'][:10]}"
        match_list.append((matchX['wyId'], match_desc))
    return match_list

match_list = get_match_list(euro_matches)


# add title for streamlit page
st.title("Soccer Events Throughout the European Championship (2016)")
# add instructions for the user
st.write("Select the match and events you want to visualize from the dropdown below:")


# Streamlit widget to select a match
match_id, match_desc = st.selectbox('Select a match:', options=match_list, format_func=lambda x: x[1])

# Filter events for the selected match
selected_match_events = [event  for event in euro_events if event['matchId'] == int(match_id)]

a_match = []
for nation in nations:
    for ev in events[nation]:
        if ev['matchId'] == match_id:
            a_match.append(ev)
            
for nation in nations:
    for match in matches[nation]:
        if match['wyId'] == match_id:
            match_f = match
            
df_a_match = pd.DataFrame(a_match)
team_1, team_2 = np.unique(df_a_match['teamId'])

team1_name = ""
team2_name = ""
for team in teams:

    if team['wyId'] == team_1:
        team1_name = team['officialName']
    if team['wyId'] == team_2:
        team2_name = team['officialName']
    
    if team1_name != "" and team2_name != "":
        break
# match team 1 name and team 2 name in df
df_a_match['teamName'] = df_a_match['teamId'].apply(lambda x: team1_name if x == team_1 else team2_name)

df_a_match['x'] = [x[0]['x'] * 1.04 for x in df_a_match['positions']]
df_a_match['y'] = [x[0]['y'] * .68 for x in df_a_match['positions']]


# Convert the selected match events to a DataFrame
df_selected_match_events = pd.DataFrame(selected_match_events)

base_plot = draw_pitch_altair()

event_options=list(df_a_match["eventName"].unique())

event_options.sort()

teams_list_name = [team1_name, team2_name]

rng = ['teal', 'mediumvioletred'] 

base_plot = draw_pitch_altair()
# write the events as a string with commas
event_options_string = ', '.join(event_options)
# list the possible events in the match
st.write(f"The possible events in the match are: {event_options_string}")

# Streamlit widget for multi-selection


selected_events = st.multiselect('Select Events:', options=event_options, default=event_options)

# Filter DataFrame based on selected events
df_a_match_filtered = df_a_match[df_a_match['eventName'].isin(selected_events)]

# Create Altair chart for the selected events
team1_chart = alt.Chart(df_a_match_filtered, title= 'Soccer Events on a True to Scale Field').mark_point().encode(
    x= alt.X('x:Q', title='Field Length (104 m)', scale=alt.Scale(domain=[0, 105]), axis=alt.Axis(tickCount=5, grid=False)),
    y=alt.Y('y:Q', title='Field Width (68 m)', scale=alt.Scale(domain=[0, 70]), axis=alt.Axis(tickCount=5, grid=False)),
    color=alt.Color('teamName:N', scale=alt.Scale(domain=teams_list_name, range=rng), title='Team'),
    shape=alt.Shape('eventName:N', title='Event Type'),
)

final_plot = base_plot + team1_chart

final_plot = final_plot.properties(width=700, height=500).configure_view(strokeWidth=0).configure_title(fontSize=30)

# Display the chart in Streamlit
st.altair_chart(final_plot, use_container_width=True)

st.write("Field Width and Length were scaled to 68m and 104m respectively to match the actual field dimensions. Originally they were represented as a percentage of the field dimensions.")