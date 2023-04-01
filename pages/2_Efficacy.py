import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime
import plotly.figure_factory as ff
import plotly.express as px
import plotly.graph_objects as go

st.sidebar.markdown("Vaccine Effficacy")
st.header("COVID-19 Vaccine Efficacy Data Manipulation")
st.markdown('''We are going to take a look at **vaccine efficacy**, which measures the effectiveness of vaccines against infection and symptomatic and severe disease (hospitalization and death). 
1. We will inspect COVID-19 vaccine efficacy summary table. The vaccine efficacy data on the table is compiled from various peer-reviewed reports and news articles since June 2021.
2. We will calculate the average efficacy for each country.''')
tab1, tab2 = st.tabs(
    ["Vaccine Efficacy Table", "Vaccine Efficacy Calculation"])
with tab1:
    st.subheader("COVID-19 Vaccine Efficacy Summary")
    df_efficacy = pd.read_excel('data/Covid-19 Vaccine Efficacy.xlsx')
    df_efficacy.Vaccine_Manufacturer = [np.nan, 'CanSino', 'Covaxin', 'Johnson&Johnson', 'Medicago', 'Moderna', 'Novavax',
                                        'Oxford/AstraZeneca', 'Pfizer/BioNTech', 'Sinopharm/Beijing', 'Sinovac', 'SKYCovione', 'Sputnik V', 'Valneva', np.nan, np.nan]
    df_efficacy_displayed = df_efficacy.loc[1:13]
    df_efficacy_displayed = df_efficacy_displayed[['Vaccine_Manufacturer', 'Severe Disease', 'Infection',
                                                   'Severe Disease.1', 'Infection.1', 'Severe Disease.2', 'Infection.2',
                                                   'Severe Disease.3', 'Infection.3', 'Severe Disease.4', 'Infection.4',
                                                   'Severe Disease.5', 'Infection.5']]
    df_efficacy_displayed.columns = ['Vaccine_Manufacturer', "Ancestral Severe Disease", "Ancestral Infection",
                                     "Alpha Severe Disease", "Alpha Infection",
                                     "Beta Severe Disease", "Beta Infection",
                                     "Gamma Severe Disease", "Gamma Infection",
                                     "Delta Severe Disease", "Delta Infection",
                                     "Omicron Severe Disease", "Omicron Infection"]
    st.caption("**Tabel1**: Covid-19 Vaccine Effectiveness at preventing")
    st.table(df_efficacy_displayed)
    st.caption(
        "source: https://www.healthdata.org/covid/covid-19-vaccine-efficacy-summary")
    st.markdown('''As we can see, 
    1. **Ancestral and Alpha** variants have the same vaccine effectiveness; 
    2. **Beta, Gamma, and Delta** variants have the same vaccine effectiveness.
    Therefore, columns for Ancestral can be dropped (Ancestral==Alpha) and columns for Alpha and Beta can be dropped (Alpha==Beta==Gamma).
    After dropping the columns, we have''')
    st.caption(
        "**Table2**: Covid-19 Vaccine Effectiveness at preventing(cleaned version)")
    st.dataframe(df_efficacy_displayed[['Vaccine_Manufacturer', "Alpha Severe Disease", "Alpha Infection", "Delta Severe Disease", "Delta Infection",
                                        "Omicron Severe Disease", "Omicron Infection"]])
    st.subheader("Vaccine Efficacy Wanes over Time")
    st.markdown('''Vaccine efficacy captures''')
    st.markdown('''
    - **the prevention of infection**: a vaccine’s efficacy at stopping transmission of the virus from one person to another. A exposed person will not contract the virus, meaning that they will not develop symptoms or disease. 
    - **the prevention of severe disease**:  a vaccine’s efficacy at preventing an exposed person from developing serious symptoms that often require hospitalization and lead to death. ''')
    tb1, tb2 = st.tabs(["Severe Disease", "Infection"])
    with tb1:
        fig1 = go.Figure()
        df_graph1 = df_efficacy_displayed[[
            "Vaccine_Manufacturer", "Alpha Severe Disease", "Delta Severe Disease", "Omicron Severe Disease"]]
        df_graph1.index = df_graph1["Vaccine_Manufacturer"]
        df_graph1.drop(["Vaccine_Manufacturer"], axis=1, inplace=True)
        for i in df_graph1.index:
            fig1.add_trace(go.Scatter(x=df_graph1.columns, y=df_graph1.loc[i, [
                "Alpha Severe Disease", "Delta Severe Disease", "Omicron Severe Disease"]], mode='lines+markers', name=i))

        fig1.update_layout(
            title="Figure 1: Vaccine Efficacy at the Prevention of Severe Disease",
            xaxis_title="COVID-19 Variants",
            yaxis_title="Vaccine Efficacy",
            legend_title="Vaccines",
        )
        st.plotly_chart(fig1, theme=None, use_container_width=True)

    with tb2:
        fig = go.Figure()
        df_graph = df_efficacy_displayed[[
            "Vaccine_Manufacturer", "Alpha Infection", "Delta Infection", "Omicron Infection"]]
        df_graph.index = df_graph['Vaccine_Manufacturer']
        df_graph.drop(["Vaccine_Manufacturer"], axis=1, inplace=True)
        for i in df_graph.index:
            fig.add_trace(go.Scatter(x=df_graph.columns, y=df_graph.loc[i, [
                "Alpha Infection", "Delta Infection", "Omicron Infection"]], mode='lines+markers', name=i))
            fig.update_layout(
                title="Figure 2: Vaccine Efficacy at the Prevention of Infection",
                xaxis_title="COVID-19 Variants",
                yaxis_title="Vaccine Efficacy",
                legend_title="Vaccines",
            )
        st.plotly_chart(fig, theme=None, use_container_width=True)


with tab2:
    st.subheader("Calculating Average Vaccine Efficiency for Each Country")
    df = pd.read_excel(
        "data/vaccinations-by-manufacturer-with-vaccine-efficacy-KM.xlsx")
    df_displayed = df.loc[1:]
    df_displayed.columns = ['Country', 'Date', 'vaccine', 'total vaccinations',
                            "Ancestral Severe Disease", "Ancestral Infection",
                            "Alpha Severe Disease", "Alpha Infection",
                            "Beta Severe Disease", "Beta Infection",
                            "Gamma Severe Disease", "Gamma Infection",
                            "Delta Severe Disease", "Delta Infection",
                            "Omicron Severe Disease", "Omicron Infection"]
    st.caption("Table 3: Vaccination Data for Countries in the World")
    st.dataframe(df_displayed)
    st.caption("Source: provided by Professor Majumder")

    all_vaccines1 = list(set(list(df["Unnamed: 2"][1:])))
    # not all vacccines can be found in a country
    all_countries = list(set(list(df["Unnamed: 0"][1:])))
    df_filtered = pd.DataFrame(columns=df.columns)
    for i in all_countries:
        all_vaccines = set(list(df[df["Unnamed: 0"] == i]["Unnamed: 2"]))
        for j in all_vaccines:
            df_filtered = pd.concat([df_filtered, df[(df["Unnamed: 0"] == i) & (
                df["Unnamed: 2"] == j)].tail(1)], axis=0)
    df_filtered = df_filtered.reset_index()

    df_filtered_display = df_filtered.copy()
    df_filtered_display.columns = ['Index', 'Country', 'Date', 'Vaccine', 'Total Vaccinations',
                                   "Ancestral Severe Disease", "Ancestral Infection",
                                   "Alpha Severe Disease", "Alpha Infection",
                                   "Beta Severe Disease", "Beta Infection",
                                   "Gamma Severe Disease", "Gamma Infection",
                                   "Delta Severe Disease", "Delta Infection",
                                   "Omicron Severe Disease", "Omicron Infection"]
    st.markdown(
        "**First**, we need to retrieve the most recent data for each country and vaccine.")
    st.caption(
        "Table 4: Filtered Vaccination Data for Countries in the World")
    st.dataframe(df_filtered_display[['Country', 'Date', 'Vaccine', 'Total Vaccinations',
                                      "Ancestral Severe Disease", "Ancestral Infection",
                                      "Alpha Severe Disease", "Alpha Infection",
                                      "Beta Severe Disease", "Beta Infection",
                                      "Gamma Severe Disease", "Gamma Infection",
                                      "Delta Severe Disease", "Delta Infection",
                                      "Omicron Severe Disease", "Omicron Infection"]])

    df_country_efficiency1 = pd.DataFrame(np.zeros((216, 15)), columns=['country', 'vaccine', 'total vaccinations',
                                                                        "Ancestral Severe Disease", "Ancestral Infection",
                                                                        "Alpha Severe Disease", "Alpha Infection",
                                                                        "Beta Severe Disease", "Beta Infection",
                                                                        "Gamma Severe Disease", "Gamma Infection",
                                                                        "Delta Severe Disease", "Delta Infection",
                                                                        "Omicron Severe Disease", "Omicron Infection"])

    df_country_efficiency1['country'] = df_filtered['Unnamed: 0']
    df_country_efficiency1['vaccine'] = df_filtered['Unnamed: 2']
    df_country_efficiency1['total vaccinations'] = df_filtered['Unnamed: 3']
    for i in range(len(df_country_efficiency1)):
        df_country_efficiency1.loc[i, ["Ancestral Severe Disease",
                                       "Ancestral Infection",
                                       "Alpha Severe Disease", "Alpha Infection",
                                       "Beta Severe Disease", "Beta Infection",
                                       "Gamma Severe Disease", "Gamma Infection",
                                       "Delta Severe Disease", "Delta Infection",
                                       "Omicron Severe Disease", "Omicron Infection"]] = df_efficacy.loc[df_efficacy['Vaccine_Manufacturer'] == df_country_efficiency1.loc[i, 'vaccine'],
                                                                                                         ['Severe Disease', 'Infection',
                                                                                                         'Severe Disease.1', 'Infection.1', 'Severe Disease.2', 'Infection.2',
                                                                                                          'Severe Disease.3', 'Infection.3', 'Severe Disease.4', 'Infection.4',
                                                                                                          'Severe Disease.5', 'Infection.5']].values.flatten().tolist()

    df_country_efficiency2 = pd.DataFrame(np.zeros((len(all_countries), 13)), columns=['country',
                                                                                       "Ancestral Severe Disease", "Ancestral Infection",
                                                                                       "Alpha Severe Disease", "Alpha Infection",
                                                                                       "Beta Severe Disease", "Beta Infection",
                                                                                       "Gamma Severe Disease", "Gamma Infection",
                                                                                       "Delta Severe Disease", "Delta Infection",
                                                                                       "Omicron Severe Disease", "Omicron Infection"])
    st.markdown(
        '''**Second**, we want to compute the average vaccine efficacy for each country, which takes a few steps:''')
    st.markdown('''
    1. we want to compute its total vaccinations **S** by summing up total vaccination for each vaccine in the country;
    2. we find the weight of each vaccine type by dividing the total vaccination for each vaccine by **S**;
    3. we find the vaccine efficacy for each variant by multiplying weights for each vaccine by corresponding vaccine efficacy and summing them up. 
    To better undertsand the steps, let us compute the vaccine efficacy for United States.
    ''')
    st.caption("Table 5: Computing Vaccine Efficacy for U.S.")
    df_temp = df_country_efficiency1[df_country_efficiency1['country']
                                     == "United States"]
    st.dataframe(df_temp)
    st.write("Computing the total vaccinations S:",
             sum(df_temp['total vaccinations']))
    st.write("Dividing the values in 'total vaccinations' column by S, we will find the corresponding weight of each vaccine:")
    sum_temp = sum(df_temp['total vaccinations'])
    st.write("**weights**=",
             list(df_temp['total vaccinations'].values/sum_temp))
    st.write("To compute the vaccine efficacy in U.S. for Ancestral Severe Disease, we multiply the weight in the 'weigtht' array by its corresponding efficacy and summing them up:", sum(np.array(df_temp['Ancestral Severe Disease'].values)
             * (df_temp['total vaccinations'].values/sum_temp)))

    for i in range(len(all_countries)):
        df_temp = df_country_efficiency1[df_country_efficiency1['country']
                                         == all_countries[i]]
        # sum of total vaccinations in the country
        sum_temp = sum(df_temp['total vaccinations'])
        df_country_efficiency2.loc[i, 'country'] = all_countries[i]
        df_country_efficiency2.loc[i, 'Ancestral Severe Disease'] = sum(np.array(
            df_temp['Ancestral Severe Disease'].values)*(df_temp['total vaccinations'].values/sum_temp))
        df_country_efficiency2.loc[i, 'Ancestral Infection'] = sum(np.array(
            df_temp['Ancestral Infection'].values)*(df_temp['total vaccinations'].values/sum_temp))
        df_country_efficiency2.loc[i, 'Alpha Severe Disease'] = sum(np.array(
            df_temp['Alpha Severe Disease'].values)*(df_temp['total vaccinations'].values/sum_temp))
        df_country_efficiency2.loc[i, 'Alpha Infection'] = sum(np.array(
            df_temp['Alpha Infection'].values)*(df_temp['total vaccinations'].values/sum_temp))

        df_country_efficiency2.loc[i, 'Beta Severe Disease'] = sum(np.array(
            df_temp['Beta Severe Disease'].values)*(df_temp['total vaccinations'].values/sum_temp))
        df_country_efficiency2.loc[i, 'Beta Infection'] = sum(np.array(
            df_temp['Beta Infection'].values)*(df_temp['total vaccinations'].values/sum_temp))
        df_country_efficiency2.loc[i, 'Gamma Severe Disease'] = sum(np.array(
            df_temp['Gamma Severe Disease'].values)*(df_temp['total vaccinations'].values/sum_temp))
        df_country_efficiency2.loc[i, 'Gamma Infection'] = sum(np.array(
            df_temp['Gamma Infection'].values)*(df_temp['total vaccinations'].values/sum_temp))
        df_country_efficiency2.loc[i, 'Delta Severe Disease'] = sum(np.array(
            df_temp['Delta Severe Disease'].values)*(df_temp['total vaccinations'].values/sum_temp))
        df_country_efficiency2.loc[i, 'Delta Infection'] = sum(np.array(
            df_temp['Delta Infection'].values)*(df_temp['total vaccinations'].values/sum_temp))

        df_country_efficiency2.loc[i, 'Omicron Severe Disease'] = sum(np.array(
            df_temp['Omicron Severe Disease'].values)*(df_temp['total vaccinations'].values/sum_temp))
        df_country_efficiency2.loc[i, 'Omicron Infection'] = sum(np.array(
            df_temp['Omicron Infection'].values)*(df_temp['total vaccinations'].values/sum_temp))

    st.markdown('''As mentioned previously, efficacy data for Ancestral and Alpha is the same and efficacy data for Beta, Gamma, and Delta is the same. 
    Therefore, we will be dropping columns for Ancestral, Beta, and Gamma. Since infection is our interest, we will be dropping columns for severe disease for each variant.
    After performing those actions, we have:''')
    st.caption(
        "Table 6: Average Vaccine Efficacy for Different Countries in the World")
    st.dataframe(df_country_efficiency2[[
        'country', 'Alpha Infection', 'Delta Infection', 'Omicron Infection']])
    df_country_efficiency2.to_csv("data/country_efficacy.csv")
