from dash import Dash, dcc, html, Input, Output, ctx
from dash import dash_table as dt
import dash_leaflet as dl
import plotly.express as px
import pandas as pd
from collections import defaultdict
import base64
from ProjectTwoCRUDModule import AnimalShelter


###########################
#    Support Functions    #
###########################
# Rename column names for higher quality presentation
def modify_heads(df_to_modify):
    heads = {str(col): str(col).replace("_", " ").title() for col in df_to_modify.columns}

    return df_to_modify.rename(columns=heads)


# Get all animals
def get_all():
    new_df = pd.DataFrame.from_records(shelter.read({})).iloc[:, 1:]
    return modify_heads(new_df)


# Get only water rescue animals
def get_water_animals():
    new_df = pd.DataFrame.from_records(shelter.read({
        "animal_type": "Dog",
        "breed": {"$in": ["Labrador Retriever Mix", "Chesapeake Bay Retriever Mix", "Newfoundland"]},
        "sex_upon_outcome": "Intact Female",
        "age_upon_outcome_in_weeks": {"$gte": 26, "$lte": 156}
    })).iloc[:, 1:]
    return modify_heads(new_df)


# Get only mountain or wilderness rescue animals
def get_mtn_animals():
    new_df = pd.DataFrame.from_records(shelter.read({
        "animal_type": "Dog",
        "breed": {
            "$in": ["German Shepherd", "Alaskan Malamute", "Old English Sheepdog", "Siberian Husky", "Rottweiler"]},
        "sex_upon_outcome": "Intact Male",
        "age_upon_outcome_in_weeks": {"$gte": 26, "$lte": 156}
    })).iloc[:, 1:]
    return modify_heads(new_df)


# Get only disaster rescue or individual tracking animals
def get_disaster_animals():
    new_df = pd.DataFrame.from_records(shelter.read({
        "animal_type": "Dog",
        "breed": {"$in": ["Doberman Pinscher", "German Shepherd", "Golden Retriever", "Bloodhound", "Rottweiler"]},
        "sex_upon_outcome": "Intact Male",
        "age_upon_outcome_in_weeks": {"$gte": 20, "$lte": 300}
    })).iloc[:, 1:]
    return modify_heads(new_df)


###########################
# Data Manipulation / Model
###########################
username = "aacuser"                            # Username for AAC database
password = "password"                           # Password for AAC database
shelter = AnimalShelter(username, password)     # Instantiate CRUD module

image_filepath = "Grazioso-Salvare-Logo.png"    # Store filepath for logo
encoded_image = base64.b64encode(               # Load image encoded for use in HTML
    open(image_filepath, 'rb').read())

df = get_all()                                  # Get all documents from AAC database


#########################
# Dashboard Layout / View
#########################
app = Dash(__name__)                            # Instantiate dash object

app.layout = html.Div([
    # Logo and Main Header
    html.Center(html.Span([
            html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), width='200'),
            html.B(html.H1('Austin Animal Shelter Dashboard', style={"margin-top": "-20px"})),
            html.P("Chris Dewey | Global Rain | SNHU CS-340")
    ])),
    html.Hr(),
    # Buttons for rescue animal filters
    html.Div(html.Center(html.Span([
                html.Label("Filter to Rescue Animals Suitable For: "),
                html.Button("Water Rescue", id="water-rescue-filter-btn", n_clicks=0),
                html.Button("Mountain or Wilderness Rescue", id="mtn-rescue-filter-btn", n_clicks=0,
                            style={"margin-left": "15px", "margin-right": "15px"}),
                html.Button("Disaster Rescue or Individual Tracking", id="disaster-rescue-filter-btn", n_clicks=0)
            ]))),
    html.Hr(),
    # Document results from AAC database in html output
    dt.DataTable(
        id='datatable-id',
        columns=[{"name": i, "id": i, "deletable": False, "selectable": True} for i in df.columns],
        data=df.to_dict('records'),
        editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        column_selectable=False,
        row_selectable="single",
        row_deletable=False,
        selected_columns=[],
        selected_rows=[0],
        page_action="native",
        page_current=0,
        page_size=10,
    ),
    # Buttons to reset rescue animal filters and reset all filters (refresh)
    html.Center(html.Span([
        html.Button("Reset Rescue Animal Filters", id="reset-filter-btn", n_clicks=0, style={"margin-right": "15px"}),
        html.A(html.Button("Reset All Filters"), href='/')
    ])),
    html.Hr(),
    # Map and graph HTML output
    html.Div(
        className='row',
        style={'display': 'flex', 'justify-content': 'center'},
        children=[html.Div(id='graph-id'), html.Div(id='map-id')]
    )
])


#############################################
# Interaction Between Components / Controller
#############################################

# Handle filter button presses
@app.callback([Output('datatable-id', 'data'),
               Output('datatable-id', 'columns')],
              [Input('water-rescue-filter-btn', 'n_clicks'),
               Input("mtn-rescue-filter-btn", "n_clicks"),
               Input("disaster-rescue-filter-btn", "n_clicks"),
               Input("reset-filter-btn", "n_clicks")])
def update_dashboard(_btn1, _btn2, _btn3, _btn4):
    button_clicked = ctx.triggered_id       # Determine ID of button pressed
    new_df = df                             # Points to existing dataframe temporarily

    match button_clicked:                   # Switch based on button id
        case 'water-rescue-filter-btn':
            new_df = get_water_animals()
        case 'mtn-rescue-filter-btn':
            new_df = get_mtn_animals()
        case 'disaster-rescue-filter-btn':
            new_df = get_disaster_animals()
        case 'reset-filter-btn':
            new_df = get_all()

    columns = [{"name": i, "id": i, "deletable": False, "selectable": True} for i in new_df.columns]
    data = new_df.to_dict('records')

    return data, columns


# Handle graph output
@app.callback(Output('graph-id', "children"),
              Input('datatable-id', "derived_viewport_data"))
def update_graphs(view_data):
    if view_data:
        graph_data = defaultdict(int)
        for animal in view_data:
            breed = animal.get("Breed")
            graph_data[breed] = graph_data.get(breed, 0) + 1

        return [dcc.Graph(figure=px.pie(df, values=graph_data.values(), names=graph_data.keys()))]


# Handle Map output
@app.callback(Output('map-id', "children"),
             [Input('datatable-id', "derived_viewport_data"),
              Input('datatable-id', 'derived_virtual_selected_rows')])
def update_map(view_data, selected_rows):
    # Determine which animal to show on map and handle errors
    if selected_rows and selected_rows[0] < len(view_data):
        selection = selected_rows[0]
    else:
        selection = 0

    # Generate map, tooltip, and popup
    if view_data:
        animal = view_data[selection]
        # Get name for map popup
        name = animal.get("Name") or "Unnamed"
        # Get list of details for map popup
        details = "\n".join(f"{key}: {val}" for key, val in animal.items())

        return [html.Center(dl.Map(
                    style={'width': '700px', 'height': '600px'},
                    center=[animal.get("Location Lat"), animal.get("Location Long")],
                    zoom=10,
                    children=[
                        dl.TileLayer(id='base-layer-id'),
                        dl.Marker(position=[animal.get("Location Lat"), animal.get("Location Long")],
                                  children=[dl.Tooltip(animal.get("Animal Id")),
                                            dl.Popup([html.H3(name), html.P(details)])])
                    ])
            )]


# Run server
if __name__ == '__main__':
    app.run_server(debug=False, dev_tools_ui=False)
