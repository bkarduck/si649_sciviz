# load up the libraries
import panel as pn
import pandas as pd
import altair as alt
# from vega_datasets import data
import json
import numpy as np

# loading the events data
events={}
nations = ['Italy','England','Germany','France','Spain','European_Championship','World_Cup']
for nation in nations:
    with open('./data/events/events_%s.json' %nation) as json_data:
        events[nation] = json.load(json_data)
        
# loading the match data
matches={}
nations = ['Italy','England','Germany','France','Spain','European_Championship','World_Cup']
for nation in nations:
    with open('./data/matches/matches_%s.json' %nation) as json_data:
        matches[nation] = json.load(json_data)

teams={}
with open('./data/teams.json') as json_data:
    teams = json.load(json_data)


# Adjusted helper function to ensure lines are closed for areas
def draw_pitch_altair():
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


match_id = 2576335
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
df_team_1 = df_a_match[df_a_match['teamId'] == team_1]
df_team_2 = df_a_match[df_a_match['teamId'] == team_2]

base_plot = draw_pitch_altair()

event_options=list(df_a_match["eventName"].unique())
# event_options=list(map(lambda x:int(x),event_options))
event_options.sort()
# event_radio=alt.binding_radio(
#     options=event_options
# )
# radio_selector = alt.selection_point(
#     name="event",
#     fields=["eventName"],
#     bind=event_radio,
#     value=event_options[0]
#     )

# team1 = alt.Chart(df_a_match).mark_point().encode(x='x', y='y', color='teamId:N').add_params(
#         radio_selector,
#     ).encode(
#         shape=alt.condition(radio_selector, alt.Shape('eventName:N', legend=None), alt.value('circle'))

#     )

teams_list_name = [team1_name, team2_name]
rng = ['red', 'blue'] 

team1 = alt.Chart(df_a_match).mark_point().encode(x='x', y='y', color=alt.Color('teamName:N', scale=alt.Scale(domain=teams_list_name, range=rng)))

final_plot = base_plot + team1



pn.extension('vega', design='bootstrap')

template = pn.template.BootstrapTemplate(
    title='Interactive Smoothing',
)

multi_choice = pn.widgets.MultiChoice(name='CheckAll', options=event_options, value=event_options)

multi_choice_row = pn.Row(multi_choice)
base_plot = draw_pitch_altair()

def final_plot1(events):
    df_a_match_filtered1 = df_a_match[df_a_match['eventName'].isin(events)]
    print(df_a_match_filtered1.shape)
    team1 = alt.Chart(df_a_match_filtered1).mark_point().encode(x='x:Q', y='y:Q',  color=alt.Color('teamName:N', scale=alt.Scale(domain=teams_list_name, range=rng)), shape = alt.Shape('eventName:N'))
    return base_plot + team1 

# chartchange = pn.panel(pn.bind(final_plot, multi_choice), watch=True)
multi_choice = pn.widgets.MultiChoice(name='Check All', options=event_options,  width=200, value=event_options)

@pn.depends(multi_choice.param.value)
def update_chart(events):
    return final_plot1(events)

layout = pn.Column(multi_choice, update_chart)
template.main.append(layout)
template.servable(title="Interactive Smoothing")
# layout.servable()

# maincol = pn.Column()
# maincol.append(chartchange)
# maincol.append(multi_choice_row)

# pn.Column(multi_choice, height=200)