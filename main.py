"""A class for controlling and displaying GUI for playing two-person normal form game"""

import re
import dash
from dash import dash_table
from dash import dcc, html
from dash import Input, Output, State
import pymongo
from game import Game
from table import Table

# Database connection
client = pymongo.MongoClient(
    "mongodb+srv://test:uToLGHDvKG87XsPC@cluster0.yejqf4u.mongodb.net/?retryWrites=true&w=majority")
db = client["mydb"]

# Global data
data = []
columns = []

app = dash.Dash("app")

# The HTML layout
app.layout = html.Div([
    html.H1("Game Theory Solver", style={'textAlign': 'center'}),
    dcc.Markdown("Game theory is the study of strategic decision-making between individuals, firms or countries."
                 " It is invented in 1944 in the published book **Theory of Games and Economic Behaviour** by von Neumann and Morgenstern."
                 " Since its first introduction, many economists and social scientists are interested"
                 " to apply theoretic analysis of game to a various real world interactions. The normal form game"
                 " is one way of modelling situation into a game using matrix. The table below"
                 " illustrates a two-person matrix game where the row corresponds to"
                 " the first player and the columnn represents the second player."
                 " The cells shows the outcome of the game when"
                 " both players independently chose a single strategy. The solution of the game"
                 " is given by its Nash equilibrium - a steady state in which neither players"
                 " can benefit by deviating from their strategies."),

    dcc.Markdown(
        "**Choose from sample games:** You can view some of the most famous examples in game theory by choosing from the list below."
        " The solution of the game will show at the bottom of the page."),

    html.Div(
        className="sample-games",
        children=[
            html.P("Sample games: "),
            dcc.Dropdown(['Battle of the sexes', 'Matching pennies', 'Prisoner\'s dilemma', 'Rock, paper, scissors',
                          'Stag hunt', 'Recently saved game..'], 'Select..',
                         id="game_examples",
                         style={'width': '240px'}),
        ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),

    dcc.Markdown("**Create your own game:** Or you can generate your own matrix game. Select the size for your matrix, "
                 "then add your own payoff values in each cells. (Note: please use comma for seperator."
                 " For example, if the payoff for the first player is 4 and "
                 " second player is 3, then it is written as 4,3.) "),

    html.Div(
        className="select-size",
        children=[
            html.P("Rows: ", style={'display': 'inline-block'}),
            dcc.Input(placeholder="row", id="row_count", type="number", max=15, min=2, value=2,
                      style={'display': 'inline-block'}),
            html.P("Cols: ", style={'display': 'inline-block'}),
            dcc.Input(placeholder="col", id="col_count", type="number", max=15, min=2, value=2,
                      style={'display': 'inline-block'}),
            html.Button("Generate", id="generate_button", n_clicks=0),
            html.Button("Solve", id="solve_button", n_clicks=0)
        ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),

    dash_table.DataTable(data=[], columns=[], id="my_table", editable=True),

    dcc.Markdown("**Calculate the game solution**: After you create your payoff matrix, "
                 "click the \"Solve\" button to see the solution of the game. It will also say"
                 " which strategies (pure or mixed) it used to solve the problem. Then, "
                 "you can save the game by clicking the \"Save\" button so you can load it the next time. "
                 "You can also reset to start over.", style={'display': 'inline-block'}),

    html.Div([
        dcc.Textarea(
            id='textarea-example',
            readOnly=True,
            value='Textarea content initialized\nwith multiple lines of text',
            style={'width': '100%', 'height': 80},
        ),
        html.Div(id='textarea-example-output', style={'whiteSpace': 'pre-line'})
    ]),

    html.Br(),
    html.Div(className="div-buttons",
             children=[
                 html.Button("Save", id="save_button", n_clicks=0, style={'display': 'inline-block'}),
                 html.A(html.Button("Reset", id="reset_button", n_clicks=0, style={'display': 'inline-block'}),
                        href='/'),
             ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),
    html.Br(),
    html.Div(id="save_message", style={'text-align': 'center'}),

    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.P("This page was built as a part of dissertation for "
           "University of Bath Computer Science year 2021/22.", style={'text-align': 'center'})
])


@app.callback(
    Output("save_message", "children"),
    Input("save_button", "n_clicks"),
    State("my_table", "data"),
    State("row_count", "value"),
    State("col_count", "value")
)
def save(n_clicks, table_data, row_value, col_value):
    """
    Insert user input data to database

    Parameters
    ----------
    n_clicks : int
        The number of count for every click event for Save button
    table_data : int
        A two-dimensional array representing the payoff matrix of both players
    row_value : int
        The row size
    col_value : int
        The col size

    Returns
    -------
    str
        A message that tells whether or not the save is successful
    """

    if n_clicks > 0:
        if table_data:
            if is_incorrect_format(table_data) or is_null_value(table_data):
                return "Save failed. Incorrect format, try again."
            else:
                t = Table(create_new=False, data=table_data, row_size=row_value, col_size=col_value)
                try:
                    t.add_records()
                    message = "\u2713 Data successfully saved."
                    return message
                except Exception as e:
                    return e.args
        else:
            return ""


@app.callback(
    Output("row_count", "value"),
    Output("col_count", "value"),
    Input("game_examples", "value")
)
def update_input(example_value):
    """
    Updates the value for the input component.

    Parameters
    ----------
    example_value : str
        The selected value in dropdown list

    Returns
    -------
    row_count : int
        the row size
    col_count : int
        the column size
    """
    if example_value:
        if example_value == 'Recently saved game..':
            t = Table()
            t.retrieve_data()
        else:
            t = Table(name=example_value)
        row_size = t.get_row_size()
        col_size = t.get_col_size()
        return row_size, col_size
    return 2,2

@app.callback(
    Output("game_examples", "value"),
    Input("generate_button", "n_clicks")
)
def update_dropdown(n_clicks):
    """
    Updates the value for the dropdown component. Set to nothing on Generate click.

    Parameters
    ----------
    n_clicks : int
        The number of count for every click event for Generate button

    Returns
    -------
    None
    """
    if (n_clicks > 0):
        return None


@app.callback(
    Output("my_table", "data"),
    Output("my_table", "columns"),
    Input("generate_button", "n_clicks"),
    Input("game_examples", "value"),
    State("row_count", "value"),
    State("col_count", "value")
)
def generate_table(n_clicks, example_value, row_count, col_count):
    """
    Populate Dash table with data

    Parameters
    ----------
    n_clicks : int
        The number of count for every click event for Generate button
    example_value : str
        The selected value in dropdown list
    row_count : int
        The row size
    col_count : str
        The column size

    Returns
    -------
    list
        The table data as required in dash table
    list
        The column name as required in dash table
    """

    global data
    global columns
    t = Table(col_size=2, row_size=2)
    data = t.get_data()
    columns = t.get_columns()

    if example_value is not None:
        if example_value == 'Recently saved game..':
            t3 = Table()
            try:
                data, columns = t3.retrieve_data()
            except Exception as e:
                return e.args
        else:
            t2 = Table(name=example_value)
            data = t2.get_data()
            columns = t2.get_columns()

        return data, columns

    if n_clicks > 0:
        print("col", col_count)
        print("row", row_count)
        t1 = Table(col_size=col_count, row_size=row_count)
        data = t1.get_data()
        columns = t1.get_columns()
        print("data", data)
        print("columns", columns)
        return data, columns

    return data, columns

@app.callback(
    Output("textarea-example", "value"),
    Input("generate_button", "n_clicks"),
    Input("solve_button", "n_clicks"),
    State("my_table", "data"),
    Input("game_examples", "value"),
    Input("my_table", "data")
)
def solve_game(generate_click, solve_click, input_data, example_value, generated_data):
    """
    Calls get_solution() function on 'Solve' button click

    Parameters
    ----------
    generate_click : int
        The number of count for every click event for Generate button
    solve_click : int
        The number of count for every click event for Solve button    input_data : array
    generated_data : array
        A payoff matrix given by the user
    example_value : None or String
        The selected value in dropdown list
    generated_data : array
        A payoff matrix with default values

    Returns
    -------
    str
        An output string
    """

    output = ''

    if solve_click > 0 and generate_click > 0:
        # print("Input data: ", input_data)
        nash = get_solution(input_data)
        return f"Game solution: {nash} "

    if example_value is not None:
        # print(example_value)
        nash = get_solution(generated_data)
        return f"Game solution: {nash} "

    return f"Game solution: {output} "


def is_null_value(input_data):
    """
    Checks for empty cells within a matrix

    Parameters
    ----------
    input_data : array
        A two-dimensional array representing the payoff matrix of both players

    Returns
    -------
    bool
        Whether or not a cell is blank
    """

    for item in input_data:
        for v in item.values():
            if v == '':
                return True
    return False


def is_incorrect_format(input_data):
    """
    Validates payoff format

    Parameters
    ----------
    input_data : array
        A two-dimensional array representing the payoff matrix of both players

    Returns
    -------
    bool
        Whether or not the typing is in the right format
        (For example 4,3).
    """
    for d in input_data:
        for item in d.items():
            print("item: ", item[1])
            match = re.search(r'^-?(\d)+,-?(\d)+$', item[1])
            if not match:
                print(match)
                return True
    return False


def get_solution(data):
    """
    Obtain the Nash equilibrium and update the text area GUI

    Parameters
    ----------
    data : array
        A two-dimensional array representing the payoff matrix of both players

    Returns
    -------
    str
        The Nash equilibrium
    """
    if is_null_value(data):
        output = 'Table cell can\'t be blank.'
    elif is_incorrect_format(data):
        output = 'Please type the payoff in the specified format.'
    else:
        g = Game(data)
        # print(p.__str__())
        output = g.solve_nash()

    return output


app.run_server(debug=True)
