import time
import dash
import pandas as pd
import plotly.express as px
from dash import dcc, html, dash_table ,no_update


from django.utils import timezone
from django.utils.termcolors import background
from django_plotly_dash import DjangoDash
from six import text_type

from diaweb.models import Glucose, Blood


def get_dates(start_date: int = 2000):
    return [i for i in range(start_date, int(timezone.now().year) + 1)]

def unix_time_millis(dt):
    return int(time.mktime(dt.timetuple()))

def unix_to_datetime(unix):
    return pd.to_datetime(unix,unit='s')

def get_marks(daterange, Nth=100):

    result = {}
    for i, date in enumerate(daterange):
        if i%Nth == 1:
            # Append value to dict
            result[unix_time_millis(date)] = str(date.strftime('%Y-%m-%d'))

    return result

app = DjangoDash('MeasurementsAnalysis')

app.layout = lambda: html.Div(children=[
    html.Fieldset(children=[
        html.Legend('Graph Types'),
        dcc.Checklist(id='graph-types',
                  options={
                      'Glucose': 'Blood Glucose',
                      'Sys': 'Blood Systolic Pressure',
                      'Dia': 'Blood Diastolic Pressure',
                      'Pulse': 'Pulse Rate',
                  }, inline=False),]
    ),
    html.Div(id='graph-properties', children=[
        html.Fieldset(children=[
          html.Legend('Graph Properties'),
          dcc.Dropdown(id='start-date', options=get_dates(), placeholder='Start Date'),
          dcc.Dropdown(id='end-date', options=get_dates(), placeholder='End Date', disabled=True),
          html.Div(id='slider-container', children=[]),
          html.Output(id='slider-output', children=[]),
        ])
    ]),
    html.Div(id='data-statistics', children=[
        html.Fieldset(children=[
            html.Legend('Data Statistics'),
            dash_table.DataTable(id='data-table',
                                 columns=[{'name': i, 'id': i} for i in ['type', 'count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']],
                                 data=[],
                                 style_cell=dict(textAlign='center'),
                                 style_header=dict(textAlign='center',
                                                   text_type='italic',
                                                   backgroundColor="cornflowerblue"),
                                 style_as_list_view=True,
                                 ),
        ])
    ]),
    html.Div(id='graph-content', children=[]),
])


@app.callback(
    dash.dependencies.Output('data-table', 'data'),
    dash.dependencies.Input('date-slider', 'value'),
    dash.dependencies.Input('graph-types', 'value'),
)
def update_data_statistics(slider_values, graph_types, *args, **kwargs):
    if graph_types is None:
        return no_update

    patient_id = kwargs['request'].session['patient_id']

    min_date = unix_to_datetime(slider_values[0])
    max_date = unix_to_datetime(slider_values[1])

    result = pd.DataFrame()

    if 'Glucose' in graph_types:
        data = Glucose.objects.filter(patient_id=patient_id, measurement_date__gte=min_date, measurement_date__lte=max_date).values('measurement',)
        try:
            df = pd.DataFrame(data).describe()
            df = df._append(pd.Series({'measurement': 'GLU'}, name="type"))

            result = result._append(df['measurement'])
        except ValueError:
            pass

    if 'Sys' in graph_types:
        data = Blood.objects.filter(measurement_date__gte=min_date, measurement_date__lte=max_date).values('systolic_pressure')
        try:
            df = pd.DataFrame(data).describe()
            df = df._append(pd.Series({'systolic_pressure': 'SYS'}, name="type"))

            result = result._append(df['systolic_pressure'])
        except ValueError:
            pass

    if 'Dia' in graph_types:
        data = Blood.objects.filter(measurement_date__gte=min_date, measurement_date__lte=max_date).values('diastolic_pressure')
        try:
            df = pd.DataFrame(data).describe()

            df = df._append(pd.Series({'diastolic_pressure': 'DIA'}, name="type"))

            result = result._append(df['diastolic_pressure'])
        except ValueError:
            pass


    if 'Pulse' in graph_types:
        data = Blood.objects.filter(measurement_date__gte=min_date, measurement_date__lte=max_date).values('pulse_rate')
        try:
            df = pd.DataFrame(data).describe()

            df = df._append(pd.Series({'pulse_rate': 'PUL'}, name="type"))

            result = result._append(df['pulse_rate'])
        except ValueError:
            pass

    return result.to_dict('records')


@app.callback(
    dash.dependencies.Output('graph-content', 'children'),
    [dash.dependencies.Input('graph-types', 'value'),
     dash.dependencies.Input('date-slider', 'value')],
)
def update_graph(graph_types, slider_values, *args, **kwargs):
    patient_id = kwargs['request'].session['patient_id']

    result = []


    if graph_types is None:
        return result

    min_date = unix_to_datetime(slider_values[0])
    max_date = unix_to_datetime(slider_values[1])

    if 'Glucose' in graph_types:
        data = Glucose.objects.filter(patient_id=patient_id, measurement_date__gte=min_date, measurement_date__lte=max_date).values('measurement', 'measurement_type', 'measurement_date')
        df = pd.DataFrame(data)
        try:
            figure = px.line(df, x='measurement_date', y='measurement', color='measurement_type')
        except ValueError:
            figure = px.line()
        result.append(dcc.Graph(id='glucose-graph', figure=figure))

    if 'Sys' in graph_types:
        data = Blood.objects.filter(patient_id=patient_id, measurement_date__gte=min_date, measurement_date__lte=max_date).values('systolic_pressure', 'measurement_date')
        df = pd.DataFrame(data)
        try:
            figure = px.line(df, x='measurement_date', y='systolic_pressure')
        except ValueError:
            figure = px.line()

        result.append(dcc.Graph(id='systolic-graph', figure=figure))

    if 'Dia' in graph_types:
        data = Blood.objects.filter(patient_id=patient_id, measurement_date__gte=min_date, measurement_date__lte=max_date).values('diastolic_pressure', 'measurement_date')
        df = pd.DataFrame(data)

        try:
            figure = px.line(df, x='measurement_date', y='diastolic_pressure')
        except ValueError:
            figure = px.line()

        result.append(dcc.Graph(id='diastolic-graph', figure=figure))

    if 'Pulse' in graph_types:
        data = Blood.objects.filter(patient_id=patient_id, measurement_date__gte=min_date, measurement_date__lte=max_date).values('pulse_rate', 'measurement_date')
        df = pd.DataFrame(data)

        try:
            figure = px.line(df, x='measurement_date', y='pulse_rate')
        except ValueError:
            figure = px.line()
        result.append(dcc.Graph(id='pulse-graph', figure=figure))

    return html.Fieldset(children=[
        html.Legend('Graphs'),
        html.Div(result)
    ]) if len(result) > 0 else []

@app.callback(
    dash.dependencies.Output('end-date', 'options'),
    dash.dependencies.Output('end-date', 'disabled'),
    dash.dependencies.Input('start-date', 'value'),
)
def update_end_date(start_date, *args, **kwargs):
    if start_date is None:
        return no_update, no_update
    return get_dates(start_date), False


@app.callback(
    dash.dependencies.Output('slider-container', 'children'),
    dash.dependencies.Input('start-date', 'value'),
    dash.dependencies.Input('end-date', 'value'),
)
def update_slider(start_date, end_date, *args, **kwargs):
    if start_date is None:
        return no_update

    if end_date is None:
        end_date = timezone.now().year

    daterange = pd.date_range(start= f'1-1-{start_date}', end= f'31-12-{end_date}', freq='1D')

    return dcc.RangeSlider(
                id='date-slider',
                min = unix_time_millis(daterange.min()),
                max = unix_time_millis(daterange.max()),
                value = [unix_time_millis(daterange.min()),
                         unix_time_millis(daterange.max())],
                marks=get_marks(daterange, len(daterange) // 5),
                allowCross=False,
            )


@app.callback(
    dash.dependencies.Output('slider-output', 'children'),
    dash.dependencies.Input('date-slider', 'value'),
)
def update_slider_output(value, *args, **kwargs):
    if value is None:
        return no_update


    return f'Start date: {unix_to_datetime(value[0])} / End date: {unix_to_datetime(value[1])}'
