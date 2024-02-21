import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd
import matplotlib.pyplot as plt
from dash import dash_table


# Load your data
car_sales = pd.read_csv("car_sales_data.csv")
car_sales['Date'] = pd.to_datetime(car_sales['Date'])

# Provided code to prepare the data
sales_performance = car_sales.groupby('Salesperson').agg(
  TotalSales=pd.NamedAgg(column='Sale Price', aggfunc='sum'),
  AverageSalePrice=pd.NamedAgg(column='Sale Price', aggfunc='mean'),
  TotalComissions=pd.NamedAgg(column='Commission Earned', aggfunc='sum')
).reset_index()

sales_performance['SalesRank'] = sales_performance['TotalSales'].rank(method='dense', ascending=False)
sales_performance['Comission_Rank'] = sales_performance['TotalComissions'].rank(method='dense', ascending=False)

N = 10
top_salespersons = sales_performance.sort_values(by='TotalSales', ascending=False).head(N)

# Define a consistent color scheme
color_scheme = {
    'background': 'white',
    'text': '#212529',
    'charts': {
        'TotalSales': '#bcbddc',
        'Commissions': '#7962bc',
        'AverageSalePrice': '#7962bc',
        'TableHeader': '#7962bc',
        'LineChart': '#7962bc',
    }
}

# Visualization code for Total Sales and Commissions with updated colors
# Rename the columns for the purpose of plotting
top_salespersons.rename(columns={'TotalSales': 'Total Sales', 'TotalComissions': 'Total Commissions'}, inplace=True)

fig = px.bar(top_salespersons,
             x='Salesperson',
             y=['Total Sales', 'Total Commissions'],  # Updated column names
             title='TOP 10 PERFORMING SALESPERSONS',
             labels={'value': 'Amount', 'variable': ''},  # Removed 'Metric' label
             barmode='group',
             color_discrete_map={
                 'Total Sales': color_scheme['charts']['TotalSales'],
                 'Total Commissions': color_scheme['charts']['Commissions']
             })

fig.update_layout(
    xaxis_title='',
    yaxis_title='Amount (Million USD)',
    xaxis={
        'categoryorder': 'total descending',
        'tickfont': dict(size=16)  # Adjust the font size as desired
    },
    title_x=0.45,  # This will center the title
    paper_bgcolor='white',
    plot_bgcolor='white',
    font=dict(family='Avenir, sans-serif'),
    title_font=dict(size=22),
    legend_font_size=16
)


# Visualization code for Average Sale Price with updated colors
fig_avg = px.bar(top_salespersons,
                 x='Salesperson',
                 y='AverageSalePrice',
                 title='AVERAGE SALE PRICE FOR TOP SALESPERSONS',
                 labels={'AverageSalePrice': 'Average Sale Price'},
                 text='AverageSalePrice',
                 color_discrete_sequence=[color_scheme['charts']['AverageSalePrice']]) # Adjusted part

fig_avg.update_layout(xaxis_title='', yaxis_title='Average Sale Price ($)',
                      xaxis={'categoryorder': 'total descending', 'tickfont': dict(size=16)}, 
                      yaxis=dict(type='log'), title_x=0.45, paper_bgcolor='white',
                      plot_bgcolor='white',
                      font=dict(family='Avenir, sans-serif'),
                      margin={'t': 50,},
                      height=500,
                      title_font=dict(size=22)
                      

                      )

fig_avg.update_traces(texttemplate='%{text:.2s}', textposition='outside',textfont_size=12)

purple_color = '#bcbddc'
# Top 5 Car Model-Year Combinations by Sales Count
sales_counts = car_sales.groupby(['Car Model', 'Car Year']).size().reset_index(name='Sales Count')
top_sales_count = sales_counts.sort_values(by='Sales Count', ascending=False).head(5)



# Donut 
car_make_counts = car_sales['Car Make'].value_counts().reset_index()
car_make_counts.columns = ['Car Make', 'Sales Count']
fig_donut = px.pie(car_make_counts, values='Sales Count', names='Car Make',
                   title="SALES DISTRIBUTION BY CAR MAKE",
                   hole=0.5
                   )

# Manually defined shades of #bcbddc
shades = [
    '#bcbddc',  # original color
    '#afa9d6',
    '#a296cf',
    '#9483c9',
    '#8770c2',
    '#7962bc',  # darker shade
]

# Apply the gradient colors to the donut chart
fig_donut.update_traces(marker_colors=shades, textposition='inside', textinfo='percent+label', insidetextfont=dict(color='#FFFFFF', size=14))
fig_donut.update_layout(showlegend=False, title_x=0.5, font=dict(family='Avenir, sans-serif'), title_font=dict(size=22))


# Visualization for Monthly Sales Trends
car_sales['Year'] = car_sales['Date'].dt.year
car_sales['Month'] = car_sales['Date'].dt.month
sales_trends = car_sales.groupby(['Year', 'Month']).size().reset_index(name='Sales Count')
sales_trends = sales_trends.sort_values(by=['Year', 'Month'])
fig_line = px.line(sales_trends, x=pd.to_datetime(sales_trends[['Year', 'Month']].assign(DAY=1)),
                   y='Sales Count',
                   title='SALES TREND FOR 2022 - 2023',
                   labels={'x': 'Date', 'Sales Count': 'Number of Sales'})

fig_line.update_layout(xaxis_title='', yaxis_title='Number of Sales',
                       xaxis=dict(tickformat='%Y-%m'), hovermode='x', title_x=0.5, paper_bgcolor='white',
                       plot_bgcolor='white', font=dict(family='Avenir, sans-serif'), title_font=dict(size=22))
fig_line.update_traces(line=dict(color=color_scheme['charts']['LineChart']))



# Initialize the Dash app with bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


# App layout with updated colors
app.layout = dbc.Container(
    [
       dbc.Row([
                dbc.Col(html.Img(src="/assets/logo.png", height="100px"), width=12, md=2, className="mb-md-0 mb-4"),  # Logo column, full width on small screens, 2 columns on medium and larger
                dbc.Col(html.H1("ANNUAL PERFORMANCE DASHBOARD", className="text-center mb-4", style={'paddingTop': '50px'}), width=12, md=10),  # H1 column, full width on small screens, 10 columns on medium and larger
            ], align="center")
        ,
        
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id='monthly-car-sales-trends', figure=fig_line), md=5, className="mb-4"),
                dbc.Col(
            [
                html.Header("MOST POPULAR CAR MODELS", style={'fontFamily': 'Avenir, sans-serif', 'fontSize': '22px','textAlign': 'center', 'paddingBottom': '30px'} ),
                dash_table.DataTable(
                    id='top-model-year-table',
                    columns=[{"name": i, "id": i} for i in top_sales_count.columns],
                    data=top_sales_count.to_dict('records'),
                    style_header={
                        'backgroundColor': color_scheme['charts']['TableHeader'],
                        'color': 'white',
                        'fontFamily': 'Avenir, sans-serif',
                        'fontWeight': 'bold',
                        'fontSize': '18px'
                    },
                    style_cell={
                        'fontFamily': 'Avenir, sans-serif',
                        'textAlign': 'left',
                        'padding': '10px',
                        'fontSize': '16px',
                        'color': color_scheme['text']  # Keep the text color
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'rgba(220, 220, 220, 0.3)',  
                        }
                    ],
                )
            ],
            md=3, className="mb-4", style={'paddingBottom': '70px'}
        ),
                dbc.Col(dcc.Graph(id='sales-distribution-by-car-make', figure=fig_donut), md=4, className="mb-4"),
            ],
            align="center",
        ),
        
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id='total-sales-commissions', figure=fig), md=6, className="mb-4"),
                dbc.Col(dcc.Graph(id='average-sale-price', figure=fig_avg), md=6, className="mb-4"),
            ],
            align="center",
        ),
        
        dbc.Row(dbc.Col(html.P("Data source: BRIGHTSTAR | Dashboard created by Ivan Manfredi | Last updated: 2024-02-19", className="text-center small-text"), width=12))
    ],
    fluid=True,
    style={'backgroundColor': color_scheme['background'], 'fontFamily': 'Avenir, sans-serif'}  # Apply the background color to the whole container
)

if __name__ == '__main__':
    app.run_server(debug=True)