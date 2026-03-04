
import streamlit as st
import pandas as pd
import plotly.express as px

#Load the CSV your notebook saved
url = 'https://drive.google.com/uc?export=download&id=1S1F5vbRakTHGxR9vxuvWpkERk3ctDDQp'
master_ds = pd.read_csv(url)

#Page config
st.set_page_config(page_title='Olist Delivery Audit', layout='wide')
st.title('Olist Delivery Audit')
st.caption(f"{len(master_ds):,} orders  ·  Python + Pandas  ·  6 Stories")

#KPI row (Story 1 + 2 outputs)
sentiment_summary = master_ds.groupby('Delivery_Status')['review_score'].mean()
on_time_count = (master_ds['Delivery_Status'] == 'On Time').sum()
late_count = master_ds['is_late'].sum()
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric('Total Orders', len(master_ds))
col2.metric('On Time', f"{on_time_count:,}", '89.1%')
col3.metric('Late + Super Late', f"{late_count:,}", '-7.9%')
col4.metric('Avg Score — On Time', f"{sentiment_summary['On Time']:.2f} ★")
col5.metric('Avg Score — Late', f"{sentiment_summary['Late']:.2f} ★", '-0.83')

st.divider()

#Row 1: Donut + Sentiment
col_a, col_b = st.columns(2)

with col_a:
    st.subheader('Delivery Status Breakdown')
    st.caption("Order counts by delivery status")
    status_counts = master_ds['Delivery_Status'].value_counts().reset_index()
    status_counts.columns = ['Delivery_Status', 'count']
    fig1 = px.pie(status_counts, values='count', names='Delivery_Status',
                  hole=0.5,
                  color_discrete_map={
                      'On Time': '#00897b',
                      'Late': '#e67e22',
                      'Super Late': '#d63031',
                      'In Progress / Unknown': '#636e72',
                      'Not Delivered': '#b2bec3'
                  })
    st.plotly_chart(fig1, use_container_width=True)

with col_b:
    st.subheader('Impact of Delays on Sentiment')
    st.caption("Average review score per delivery status")
    sentiment = master_ds.groupby('Delivery_Status')['review_score'].mean().reset_index()
    sentiment.columns = ['Delivery_Status', 'avg_score']
    sentiment = sentiment.sort_values('avg_score', ascending=True)
    fig2 = px.bar(sentiment, x='avg_score', y='Delivery_Status',
                  orientation='h', text='avg_score',
                  color='avg_score',
                  color_continuous_scale='RdYlGn',
                  range_x=[0, 5])
    fig2.update_traces(texttemplate='%{text:.2f}')
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

#Row 2: Heatmap (Story 3)──
st.subheader('% Late Deliveries by State (Sorted)')
st.caption("Late delivery rate per state, sorted highest to lowest")
state_late = master_ds.groupby('customer_state')['is_late'].mean().mul(100).round(1)
state_late = state_late.reset_index()
state_late.columns = ['State', 'Late %']
state_late = state_late.sort_values('Late %', ascending=False)
fig3 = px.bar(state_late, x='State', y='Late %',
              color='Late %',
              color_continuous_scale='Reds',
              text='Late %')
fig3.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
st.plotly_chart(fig3, use_container_width=True)

# Remote vs Near SP
col_c, col_d, col_e = st.columns(3)
near_sp_states = ["SP", "RJ", "MG", "ES"]
master_ds["is_remote"] = ~master_ds["customer_state"].isin(near_sp_states)
remote_vs_near = master_ds.groupby("is_remote")["is_late"].mean() * 100
col_c.metric('Near SP Late Rate', f"{remote_vs_near[False]:.2f}%")
col_d.metric('Remote States Late Rate', f"{remote_vs_near[True]:.2f}%")
col_e.metric('Remote is', f"{remote_vs_near[True]/remote_vs_near[False]:.1f}× worse")

st.divider()

#Row 3: Sellers (Story 6)
col_f, col_g = st.columns(2)

with col_f:
    st.subheader('Top 10 Sellers by Late Rate')
    st.caption("Sellers with at least 10 orders, ranked by late rate")
    seller_stats = master_ds.groupby('seller_id').agg(
        late_rate=('is_late', 'mean'),
        total_orders=('order_id', 'count')
    ).reset_index()
    seller_stats['late_rate'] = seller_stats['late_rate'] * 100
    top10 = seller_stats[seller_stats['total_orders'] >= 10]
    top10 = top10.sort_values('late_rate', ascending=False).head(10)
    top10['seller_id'] = top10['seller_id'].str[:12] + '...'
    fig4 = px.bar(top10, x='late_rate', y='seller_id',
                  orientation='h', text='late_rate',
                  color='late_rate', color_continuous_scale='Reds')
    fig4.update_traces(texttemplate='%{text:.1f}%')
    st.plotly_chart(fig4, use_container_width=True)

with col_g:
    st.subheader('Seller Volume Distribution')
    st.caption("Statistical breakdown of how many orders each seller handles")
    seller_vol = master_ds.groupby('seller_id')['order_id'].count()
    desc = seller_vol.describe(percentiles=[.5,.75,.9,.95,.99])
    st.dataframe(desc.round(2).to_frame('Orders per Seller'),
                 use_container_width=True)

st.divider()
