import streamlit as st
from PIL import Image
import pandas as pd
import base64
import matplotlib.pyplot as plt
import requests

# ---------------------------------#
# New feature (make sure to upgrade your streamlit library)
# pip install --upgrade streamlit

# ---------------------------------#
# Page layout
## Page expands to full width

st.set_page_config(
    page_title="Crypto Price App",
    page_icon="💷",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/ASAinit',
        'Report a bug': "https://github.com/ASAinit",
        'About': "#This web application retrieves cryptocurrency prices for the top 100 cryptocurrencies from CoinMarketCap. Users can select a currency for price comparison, choose cryptocurrencies to display, and sort data as needed. It also allows users to search for a specific cryptocurrency and view a candlestick chart of its historical data."
    }
)

# ---------------------------------#
# Title
image = Image.open('logo.jpg')

st.image(image, width=600)

st.header('Crypto Price App', divider='rainbow')
st.subheader(
    ':rainbow[This app retrieves cryptocurrency prices for the top 100 cryptocurrency from the **CoinMarketCap**! ] ')

# ---------------------------------#
# About
expander_bar = st.expander("**About**")
expander_bar.markdown("""
*:orange[Usage:]* This web application retrieves cryptocurrency prices for the top 100 cryptocurrencies from CoinMarketCap. Users can select a currency for price comparison, choose cryptocurrencies to display, and sort data as needed. It also allows users to search for a specific cryptocurrency and view a candlestick chart of its historical data.

*:orange[Created By:]* :blue[Aditya Singh Amber]  from the B.C.A course at Jeevandeep Mahavidyalya.
""")

# ---------------------------------#
# Page layout (continued)
## Divide page into 3 columns (col1 = sidebar, col2 and col3 = page contents)
col1 = st.sidebar
col2, col3 = st.columns((2, 1))

# ---------------------------------#
# Sidebar + Main panel
col1.markdown(''':violet[Input Options]''')

## Sidebar - Currency price unit
currency_price_unit = col1.selectbox('Select currency for price', ('USD', 'BTC', 'ETH'))

# Enter your CoinMarketCap API key here
api_key = '58c2d26e-6b17-4a26-933b-625fef84e704'  # Replace with your actual API key

# Make API requests to CoinMarketCap
def load_data():
    # Define the API URL
    api_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'

    # Define the parameters for the API request
    params = {
        'start': '1',
        'limit': '100',
        'convert': currency_price_unit  # Use the selected currency unit
    }

    # Set the API key in the headers
    headers = {
        'X-CMC_PRO_API_KEY': api_key
    }

    # Make the API request
    response = requests.get(api_url, params=params, headers=headers)

    # Parse the JSON response
    data = response.json()

    # Extract cryptocurrency data
    cryptocurrencies = data['data']

    coin_name = []
    coin_symbol = []
    market_cap = []
    percent_change_1h = []
    percent_change_24h = []
    percent_change_7d = []
    price = []
    volume_24h = []

    for crypto in cryptocurrencies:
        coin_name.append(crypto['name'])
        coin_symbol.append(crypto['symbol'])
        price.append(crypto['quote'][currency_price_unit]['price'])
        percent_change_1h.append(crypto['quote'][currency_price_unit]['percent_change_1h'])
        percent_change_24h.append(crypto['quote'][currency_price_unit]['percent_change_24h'])
        percent_change_7d.append(crypto['quote'][currency_price_unit]['percent_change_7d'])
        market_cap.append(crypto['quote'][currency_price_unit]['market_cap'])
        volume_24h.append(crypto['quote'][currency_price_unit]['volume_24h'])

    df = pd.DataFrame(
        columns=['coin_name', 'coin_symbol', 'marketCap', 'percentChange1h', 'percentChange24h', 'percentChange7d',
                 'price', 'volume24h'])
    df['coin_name'] = coin_name
    df['coin_symbol'] = coin_symbol
    df['price'] = price
    df['percentChange1h'] = percent_change_1h
    df['percentChange24h'] = percent_change_24h
    df['percentChange7d'] = percent_change_7d
    df['marketCap'] = market_cap
    df['volume24h'] = volume_24h

    return df

df = load_data()

## Sidebar - Cryptocurrency selections
sorted_coin = sorted(df['coin_symbol'])
selected_coin = col1.multiselect('Cryptocurrency', sorted_coin, sorted_coin)

df_selected_coin = df[df['coin_symbol'].isin(selected_coin)]  # Filtering data

## Sidebar - Number of coins to display
num_coin = col1.slider('Display Top N Coins', 1, 100, 100)
df_coins = df_selected_coin[:num_coin]

## Sidebar - Percent change timeframe
percent_timeframe = col1.selectbox('Percent change time frame', ['7d', '24h', '1h'])
percent_dict = {"7d": 'percentChange7d', "24h": 'percentChange24h', "1h": 'percentChange1h'}
selected_percent_timeframe = percent_dict[percent_timeframe]

## Sidebar - Sorting values
sort_values = col1.selectbox('Sort values?', ['Yes', 'No'])

col2.subheader('Price Data of Selected Cryptocurrency')
col2.write(f'Data Dimension: {df_selected_coin.shape[0]} rows and {df_selected_coin.shape[1]} columns.')
col2.dataframe(df_coins)

# Create a function to download CSV data
def download_csv(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # Convert to base64
    href = f'data:file/csv;base64,{b64}'  # Data URI
    return href

# Display a download button for CSV data
csv_data = download_csv(df_selected_coin)

col2.markdown(
    f'<a href="{csv_data}" download="crypto.csv">'
    '<button class="p-Widget jupyter-widgets jupyter-button widget-button mod-info" style="cursor: pointer;">'
    'Download CSV'
    '</button></a>',
    unsafe_allow_html=True
)

# ---------------------------------#
# Preparing data for Bar plot of % Price change
col2.subheader('Table of % Price Change',)
df_change = df_coins[['coin_symbol', 'percentChange1h', 'percentChange24h', 'percentChange7d']].copy()
df_change.set_index('coin_symbol', inplace=True)
df_change['positive_percent_change_1h'] = df_change['percentChange1h'] > 0
df_change['positive_percent_change_24h'] = df_change['percentChange24h'] > 0
df_change['positive_percent_change_7d'] = df_change['percentChange7d'] > 0
col2.dataframe(df_change)

# Conditional creation of Bar plot (time frame)
col3.subheader('Bar plot of % Price Change')

if percent_timeframe == '7d':
    if sort_values == 'Yes':
        df_change = df_change.sort_values(by=['percentChange7d'])
    col3.write('*7 days period*')
    plt.figure(figsize=(5, 25))
    plt.subplots_adjust(top=1, bottom=0)
    df_change['percentChange7d'].plot(kind='barh',
                                      color=df_change.positive_percent_change_7d.map({True: 'g', False: 'r'}))
    col3.pyplot(plt)
elif percent_timeframe == '24h':
    if sort_values == 'Yes':
        df_change = df_change.sort_values(by=['percentChange24h'])
    col3.write('*24 hour period*')
    plt.figure(figsize=(5, 25))
    plt.subplots_adjust(top=1, bottom=0)
    df_change['percentChange24h'].plot(kind='barh',
                                       color=df_change.positive_percent_change_24h.map({True: 'g', False: 'r'}))
    col3.pyplot(plt)
else:
    if sort_values == 'Yes':
        df_change = df_change.sort_values(by=['percentChange1h'])
    col3.write('*1 hour period*')
    plt.figure(figsize=(5, 25))
    plt.subplots_adjust(top=1, bottom=0)
    df_change['percentChange1h'].plot(kind='barh',
                                      color=df_change.positive_percent_change_1h.map({True: 'g', False: 'r'}))
    col3.pyplot(plt)
