import os
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
import geopandas as gpd


def resource_path(*parts):
    return os.path.join(Path(__file__).resolve().parent, 'data', *parts)


@st.cache_data
def load_state_sales(csv_path):
    return pd.read_csv(csv_path)


@st.cache_data
def load_price_history(csv_path):
    df = pd.read_csv(csv_path)
    df['Month'] = df['Month'].astype(str)
    df['date'] = pd.to_datetime(df['Year'].astype(str) + '-' + df['Month'], format='%Y-%b', errors='coerce')
    df = df.dropna(subset=['date']).sort_values('date')
    return df


def main():
    st.set_page_config(page_title='Silver App ', layout='wide')
    st.title('Silver Price Calculator & Sales Dashboard ')

    sales_csv = resource_path('state_wise_silver_purchased_kg.csv')
    price_csv = resource_path('historical_silver_price.csv')

    sales_df = load_state_sales(sales_csv)
    price_df = load_price_history(price_csv)

    left, right = st.columns(2)

    with left:
        st.header('Silver Price Calculator')
        unit = st.selectbox('Weight unit', ['grams', 'kilograms'])
        weight = st.number_input('Weight', min_value=0.0, value=100.0)
        price_per_gram = st.number_input('Price per gram (INR)', min_value=0.0, value=50.0)
        currency = st.selectbox('Currency', ['INR', 'USD'])
        rate = 0.11

        grams = weight if unit == 'grams' else weight * 1000
        total_inr = grams * price_per_gram
        total = total_inr if currency == 'INR' else total_inr * rate

        st.write(f'Calculated Price : {total:,.2f} {currency}')

        st.markdown('---')
        st.subheader('Historical Silver Price (INR/kg)')
        option = st.radio('Filter', ['All', 'less than 20,000 INR per kg', 'Between 20,000 and 30,000 INR per kg', 'greater than 30,000 INR per kg'])
        h = price_df.copy()
        if option == 'less than 20,000 INR per kg':
            h = h[h['Silver_Price_INR_per_kg'] <= 20000]
        elif option == 'Between 20,000 and 30,000 INR per kg':
            h = h[(h['Silver_Price_INR_per_kg'] > 20000) & (h['Silver_Price_INR_per_kg'] < 30000)]
        elif option == 'greater than 30,000 INR per kg':
            h = h[h['Silver_Price_INR_per_kg'] >= 30000]

        fig = px.line(h, x='date', y='Silver_Price_INR_per_kg', title='Historical Silver Price (INR/kg)', labels={'date': 'Date', 'Silver_Price_INR_per_kg': 'Silver Price (INR/kg)'})
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.header('Sales Dashboard ')
        st.subheader('State purchases')
        st.dataframe(sales_df)

        st.subheader('Top 5 states')
        top5 = sales_df.nlargest(5, 'Silver_Purchased_kg')
        fig2 = px.bar(top5, x='State', y='Silver_Purchased_kg', title='Top 5 States by Silver Purchased (kg)')
        st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Purchases in the month of January")
        k = price_df[price_df['Month'] == 'Jan']
        fig3 = px.line(k, x='Year', y='Silver_Price_INR_per_kg', title='Silver Price in January by Year', labels={'Year': 'Year', 'Silver_Price_INR_per_kg': 'Silver Price (INR/kg)'})
        st.plotly_chart(fig3, use_container_width=True)



if __name__ == '__main__':
    main()

