import geopandas as gpd
import pandas as pd
import json
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

# CARGAR Y PREPARAR DATOS

# Cargar archivo KML
gdf = gpd.read_file("MUNICIPIOS CON NOMBRE.kml", driver='KML')
gdf = gdf[['Name', 'geometry']]

# Cargar Excel
df = pd.read_excel("CLIMA PRUEBAS 2001.xlsx")

# Unir GeoDataFrame con DataFrame
gdf_merged = gdf.merge(df, left_on='Name', right_on='MUNICIPIO', how='left')

# Convertir a GeoJSON
geojson_data = json.loads(gdf_merged.to_json())

# Lista de años disponibles
years = sorted(df['AÑO'].unique())

# CONFIGURAR DASH APP

app = Dash(__name__)
server = app.server

app.title = "Mapa Climático Interactivo"

app.layout = html.Div([
    html.H2("Mapa Climático por Municipio y Año", style={'textAlign': 'center'}),
    
    html.Div([
        html.Label("Selecciona variable:"),
        dcc.Dropdown(
            id='variable-dropdown',
            options=[
                {'label': 'Temperatura Promedio', 'value': 'TEMPERATURA'},
                {'label': 'Temperatura Mínima', 'value': 'TEMP_MIN'},
                {'label': 'Temperatura Máxima', 'value': 'TEMP_MAX'},
                {'label': 'Precipitaciones', 'value': 'PRECIPITACIONES'},
            ],
            value='TEMPERATURA',
            clearable=False,
            style={'width': '300px'}
        )
    ], style={'textAlign': 'center', 'marginBottom': '20px'}),
    
    html.Div([
        dcc.Graph(id='mapa-climatico', style={'height': '80vh'})
    ]),
    
    html.Div([
        dcc.Slider(
            id='year-slider',
            min=min(years),
            max=max(years),
            value=min(years),
            marks={int(year): str(int(year)) for year in years},
            step=None
        )
    ], style={'padding': '0px 50px 20px 50px'})
])

# CALLBACKS INTERACTIVOS

@app.callback(
    Output('mapa-climatico', 'figure'),
    [Input('variable-dropdown', 'value'),
     Input('year-slider', 'value')]
)
def update_map(variable, year):
    df_year = gdf_merged[gdf_merged['AÑO'] == year]
    
    fig = px.choropleth_mapbox(
        df_year,
        geojson=geojson_data,
        locations='MUNICIPIO',
        featureidkey="properties.MUNICIPIO",
        color=variable,
        color_continuous_scale='RdYlBu_r' if 'TEMP' in variable else 'YlGnBu',
        hover_name='MUNICIPIO',
        hover_data={
            'AÑO': True,
            'TEMPERATURA': True,
            'TEMP_MIN': True,
            'TEMP_MAX': True,
            'PRECIPITACIONES': True
        },
        mapbox_style="carto-positron",
        center={"lat": -16.29, "lon": -63.58},  # centro aproximado de Bolivia
        zoom=5,
        opacity=0.8,
    )

    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        coloraxis_colorbar=dict(title=variable),
        title=f"{variable} en el año {year}"
    )
    return fig

# EJECUTAR APLICACIÓN


if __name__ == '__main__':
    app.run_server(debug=True) 