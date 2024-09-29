import dash
import pandas as pd
import plotly.express as px
from dash import dcc, html

from django_plotly_dash import DjangoDash

from diaweb.models import Glucose, Blood

app = DjangoDash('SimpleExample')

app.layout = lambda: html.Div(children=[
    html.Div(id='dummy'),
    html.H2(children='Hello world'),
    html.Div(id='test',),
    dcc.Graph(id='Example')

])


@app.callback(
    dash.dependencies.Output('Example', 'figure'),
    [dash.dependencies.Input('dummy', 'children')]
)
def update_graph(*args, **kwargs):
    patient_id = kwargs['request'].session['patient_id']
    data = Glucose.objects.filter(patient_id=patient_id).values('measurement', 'measurement_type', 'measurement_date')
    df = pd.DataFrame(data)

    figure = px.line(df, x='measurement_date', y='measurement', color='measurement_type')
    return figure
