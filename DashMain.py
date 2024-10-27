import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import requests
import datetime
import time

# OpenWeatherMap API details
API_KEY = '23b61c0879126be6a598f9964f2b1b87'
CITY = "Perth"
UNITS = "metric"  # 'metric' for Celsius

# Initialize the Dash app with a Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Function to fetch weather data
def get_weather_forecast():
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={CITY}&units=metric&appid={API_KEY}"
    
    response = requests.get(url)
    data = response.json()

    # Debugging: Print the raw data response for inspection
    print("API Response:", data)  # Add this line to see the response structure

    if response.status_code == 200:
        daily_forecast = {}
        
        # Iterate through the forecast entries
        for entry in data['list']:
            dt_txt = entry['dt_txt']
            date = dt_txt.split(" ")[0]  # Extract date
            temp = entry['main']['temp']
            weather_description = entry['weather'][0]['description']
            icon = entry['weather'][0]['icon']  # Get the icon code
            icon_url = f"http://openweathermap.org/img/wn/{icon}.png"  # Construct URL for icon
            # Group by date and find the maximum temperature
            if date not in daily_forecast:
                daily_forecast[date] = {
                    'max_temp': temp,
                    'description': weather_description,
                    'icon_url': icon_url
                }
            else:
                daily_forecast[date]['max_temp'] = max(daily_forecast[date]['max_temp'], temp)

        return daily_forecast  # Ensure it returns a dictionary
    else:
        print(f"Error: {response.status_code}, {data}")  # Print error information
        return {}  # Return an empty dictionary on error

# Fetch the weather forecast data
forecast_data = get_weather_forecast()

# Get current time
def get_current_time():
    return datetime.datetime.now().strftime('%H:%M')

# Define the layout of the app
app.layout = dbc.Container(
    [
        html.H1("Home", style={"textAlign": "center"}),
        html.Div(id='clock', style={'fontSize': '72px', 'textAlign': 'center'}),
        
        html.Div([
            html.H3("", style={'textAlign': 'center'}),
            dbc.Row([
                dbc.Col(
                    html.Div(
                        [
                            html.Div(f"{datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%a')}", style={"fontWeight": "bold"}),
                            html.Img(src=forecast['icon_url'], style={"height": "50px", "width": "50px"}),
                            html.Div(f"{forecast['max_temp']}°C", style={"fontSize": "20px"}),
                            html.Div(f"{forecast['description'].capitalize()}", style={"fontSize": "16px"})
                        ],
                        style={"textAlign": "center", "margin": "10px"}
                    ),
                    width=2
                ) for date, forecast  in forecast_data.items()
            ]),
        ], style={'display': 'flex', 'justifyContent': 'center'}),
        
        html.Div([
            html.Div(id='calendar', style={'fontSize': '36px', 'textAlign': 'center', 'margin': '10px', 'border': '1px solid black', 'padding': '10px'})
        ]),
    ],
    fluid=True,
)

# Update the clock every second
@app.callback(
    dash.dependencies.Output('clock', 'children'),
    [dash.dependencies.Input('interval-component', 'n_intervals')]
)
def update_clock(n):
    return get_current_time()

# Periodically update the clock
app.layout.children.append(dcc.Interval(id='interval-component', interval=1000, n_intervals=0))

# Update calendar display
@app.callback(
    dash.dependencies.Output('calendar', 'children'),
    [dash.dependencies.Input('interval-component', 'n_intervals')]
)
def update_calendar(n):
    today = datetime.datetime.now().strftime('%d %B, %Y')
    return today

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
