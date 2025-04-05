from mftool import Mftool
import streamlit as st, numpy as np, pandas as pd, plotly.express as ps

mf=Mftool()

st.title('Mutual Fund Financial Dashboard')

#the drop down menu
option=st.sidebar.selectbox(
    "Choose an action",
    ["View Available Schemes","Scheme Details","Historical NAV","Compare NAVs","Average AUM","Performance Heatmap","Risk & Volatility Analysis"]) 

#Fetch all scheme codes
scheme_names= {v:k for k, v in mf.get_scheme_codes().items()}

if option == 'View Available Schemes':
    st.header('View Available Schemes')
    amc=st.sidebar.text_input("Enter AMC Name","ICICI")
    schemes= mf.get_available_schemes(amc)
    st.write(pd.DataFrame(schemes.items(),columns=['Scheme Code','Scheme Name']) if schemes else "No Scheme found")

if option == 'Scheme Details':
    st.header('Scheme Details')
    scheme_code= scheme_names[st.sidebar.selectbox('Select a Scheme', scheme_names.keys())]
    details= pd.DataFrame(mf.get_scheme_details(scheme_code)).iloc[0]
    st.write(details)

if option == 'Historical NAV':
    st.header('Historical NAV')
    scheme_code= scheme_names[st.sidebar.selectbox('Select a Scheme', scheme_names.keys())]
    nav_data = mf.get_scheme_historical_nav(scheme_code, as_Dataframe=True)
    st.write(nav_data)

if option == 'Compare NAVs':
    st.header('Compare NAVs')
    selected_schemes= st.sidebar.multiselect('Select Schemes to Compare', options=list(scheme_names.keys()))
    if selected_schemes:
        comparison_df = pd.DataFrame()
        for scheme in selected_schemes:
            code = scheme_names[scheme]
            data = mf.get_scheme_historical_nav(code, as_Dataframe=True)
            data = data.reset_index().rename(columns={'index':'date'})
            data['date'] = pd.to_datetime(data['date'],dayfirst=True).sort_values()
            data['nav'] = data['nav'].replace(0, None).interpolate()
            comparison_df[scheme] = data.set_index('date')['nav']
        fig = ps.line(comparison_df, title='Comparison of NAVs')
        st.plotly_chart(fig)
    else:
        st.info("Select at least one scheme")

if option == 'Average AUM':
    st.header('Average AUM')
    aum_data = mf.get_average_aum('July - September 2024', False)
    if aum_data:
        aum_df= pd.DataFrame(aum_data)
        aum_df['Total AUM'] = aum_df[['AAUM Overseas', 'AAUM Domestic']].astype(float).sum(axis=1)
        st.write(aum_df[['Fund Name', 'Total AUM']])
    else:
        st.write('No AUM data avavilable')

if option == 'Performance Heatmap':
    st.header('Performance Heatmap')
    scheme_code = scheme_names[st.sidebar.selectbox('Select a Scheme', scheme_names.keys())]
    nav_data = mf.get_scheme_historical_nav(scheme_code, as_Dataframe=True)
    if not nav_data.empty:
        nav_data = nav_data.reset_index().rename(columns={'index':'date'})
        nav_data['month'] = pd.DatetimeIndex(nav_data['date']).month
        nav_data['nav'] = nav_data['nav'].astype(float)
        #st.write(nav_data)
        heatmap_data = nav_data.groupby('month')['dayChange'].mean().reset_index()
        heatmap_data['month'] = heatmap_data['month'].astype(str)
        fig = ps.density_heatmap(heatmap_data, x="month", y="dayChange", title="NAV Performance Heatmap", color_continuous_scale='viridis')
        st.plotly_chart(fig)
    else:
        st.write('No historical NAV date avvailable')

if option == 'Risk & Volatility Analysis':
    st.header('Risk & Volatility Analysis')
    scheme_name = st.sidebar.selectbox('Select a Scheme', scheme_names.keys())
    scheme_code = scheme_names[scheme_name]
    nav_data = mf.get_scheme_historical_nav(scheme_code, as_Dataframe=True)

    if not nav_data.empty:
        nav_data = nav_data.reset_index().rename(columns={'index':'data'})
        nav_data['date'] = pd.to_datetime(nav_data['date'], dayfirst=True)

        nav_data['nav'] = pd.to_numeric(nav_data['nav'], errors='coerce')
        nav_data = nav_data.dropna(subset=['nav'])

        nav_data['returns'] = nav_data['nav']/nav_data['nav'].shift(-1) - 1
        nav_data = nav_data.dropna(subset=['returns'])

        annualized_volatility = nav_data['returns'].std() * np.sqrt(252)
        annualized_return = (1 + nav_data['returns'].mean())**252 - 1

        risk_free_rate = 0.06
        sharpe_ratio = (annualized_return - risk_free_rate) / annualized_volatility
        st.write(f"### Metrics for {scheme_name}")
        st.metric('Annualized Return', f"{annualized_return: .2%}")
        st.metric('Sharpe Ratio', f"{sharpe_ratio:.2f}")





