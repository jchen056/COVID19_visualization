import streamlit as st
import pandas as pd
import numpy as np
import geopandas
import plotly.express as px
import plotly.graph_objects as go
from streamlit_folium import st_folium
from plotly.subplots import make_subplots

st.header("Breakthrough COVID-19 Infection")
st.sidebar.markdown("Breakthrough Infection")
st.markdown("""Previously, we have computed (1)**% People Fully Vaccinated** and (2)**Average Vaccine Efficacy** for Different Countries in the World.
In this section, we are going to compute the breakthrough infection and visualize breakthrough infection.""")


tab1, tab2, tab3 = st.tabs(
    ["Datasets Combination", "Compute Breakthrough Infection", "Visualize Breakthrough Infection"])
with tab1:
    st.subheader("Datasets Combination")
    df_test = pd.read_csv("data/world_dataset.csv")
    df_test = df_test[['pop_est', 'continent', 'name', 'ISO3', 'gdp_md_est',
                       'geometry', 'gdp_per_cap', '% People Fully Vaccinated',
                       '% People Vaccinated']]
    df_test["Alpha Infection Efficacy"] = np.nan
    df_test["Delta Infection Efficacy"] = np.nan
    df_test["Omicron Infection Efficacy"] = np.nan

    st.markdown("""**First**, we will combine the world dataset with the average vaccine efficacy dataset using **left join**. Left join will make sure that we can keep all the data in the world dataset.""")
    df_temp = pd.read_csv("data/country_efficacy.csv")
    df_temp = df_temp[['country', 'Alpha Infection',
                       'Delta Infection', 'Omicron Infection']]
    df_temp.loc[1, ['country']] = "United States of America"
    country_efficacy = list(df_temp.country)
    with st.expander("Clicked here to view combined dataset"):
        for i in range(df_test.shape[0]):
            country = df_test.loc[i]["name"]
            if country in country_efficacy:
                df_test.at[i, "Alpha Infection Efficacy"] = df_temp[df_temp["country"]
                                                                    == country]["Alpha Infection"].values[0]
                df_test.at[i, "Delta Infection Efficacy"] = df_temp[df_temp["country"]
                                                                    == country]["Delta Infection"].values[0]
                df_test.at[i, "Omicron Infection Efficacy"] = df_temp[df_temp["country"]
                                                                      == country]["Omicron Infection"].values[0]
        df_test = df_test[df_test["name"] != "Eritrea"]
        st.dataframe(df_test)
    st.markdown("""
    As we can see, there are a lot of null values for columns 'Alpha Infection Efficacy','Delta Infection Efficacy',and 'Omicron Infection Efficacy', which makes sense.
    """)
    st.write("- The length of world dataset is ", len(df_test), '.')
    st.write("- The length of average vaccine efficacy dataset is ",
             len(df_temp), '.')
    st.write(
        "Therefore, we do not have average vaccine efficacy data for a lot of countries.")

    world = geopandas.read_file(
        geopandas.datasets.get_path('naturalearth_lowres'))
    world.rename(columns={'iso_a3': 'ISO3'}, inplace=True)
    world['gdp_per_cap'] = world.gdp_md_est / world.pop_est
    world["Persons_Fully_Vaccinated"] = np.nan
    world["persons_vaccinated"] = np.nan
    df_vaccine = pd.read_excel(
        'data/vaccination-data-WHO-12-28-2022-NO-DETAILS for-vaciinetype-date.xlsx')
    df_vaccine = df_vaccine[df_vaccine["COUNTRY"] != "Eritrea"]
    for i in range(world.shape[0]):
        iso_code = world.loc[i]["ISO3"]
        if iso_code in list(df_vaccine["ISO3"]):
            world.at[i, "Persons_Fully_Vaccinated"] = df_vaccine[df_vaccine["ISO3"]
                                                                 == iso_code].iloc[0]["PERSONS_FULLY_VACCINATED"]
            world.at[i, "persons_vaccinated"] = df_vaccine[df_vaccine["ISO3"]
                                                           == iso_code].iloc[0]["PERSONS_VACCINATED_1PLUS_DOSE"]
    world = world[(world.pop_est > 0) & (world.name != "Antarctica")]
    # world.dropna(inplace=True)
    world["% People Fully Vaccinated"] = world['Persons_Fully_Vaccinated'] / \
        world['pop_est']*100
    world["% People Vaccinated"] = world['persons_vaccinated'] / \
        world['pop_est']*100
    world.index = range(len(world))
    for i in range(world.shape[0]):
        country = world.loc[i]["name"]
        if country in country_efficacy:
            world.at[i, "Alpha Infection Efficacy"] = df_temp[df_temp["country"]
                                                              == country]["Alpha Infection"].values[0]
            world.at[i, "Delta Infection Efficacy"] = df_temp[df_temp["country"]
                                                              == country]["Delta Infection"].values[0]
            world.at[i, "Omicron Infection Efficacy"] = df_temp[df_temp["country"]
                                                                == country]["Omicron Infection"].values[0]

    with st.expander("Click here to visualize the distribution for average vaccine efficacy"):
        option = st.selectbox(
            'Select the average vaccine efficacy data for one variant:',
            ("Alpha Infection Efficacy", "Delta Infection Efficacy", "Omicron Infection Efficacy"))
        st.write("You will be visualizing the distribution for", option, '.')
        if option == "Alpha Infection Efficacy":
            st_folium(world.explore(column="Alpha Infection Efficacy",
                                    cmap="YlGn",
                                    tiles="CartoDB positron",
                                    tooltip='name',
                                    popup=['name', 'pop_est', '% People Fully Vaccinated', "Alpha Infection Efficacy", "Delta Infection Efficacy", "Omicron Infection Efficacy"]))
        elif option == "Delta Infection Efficacy":
            m1 = world.explore(column="Delta Infection Efficacy",
                               cmap="YlGn",
                               tiles="CartoDB positron",
                               tooltip='name',
                               popup=['name', 'pop_est', '% People Fully Vaccinated', "Alpha Infection Efficacy", "Delta Infection Efficacy", "Omicron Infection Efficacy"])
            st_folium(m1)
        else:
            st_folium(world.explore(column="Omicron Infection Efficacy",
                                    cmap="YlGn",
                                    tiles="CartoDB positron",
                                    tooltip='name',
                                    popup=['name', 'pop_est', '% People Fully Vaccinated', "Alpha Infection Efficacy", "Delta Infection Efficacy", "Omicron Infection Efficacy"]))


with tab2:
    st.subheader("Compute Breakthrough Infection")
    st.markdown("""**Second**, we will compute the **Breakthrough Infection** by subtracting **'Infection Efficacy'** from 1. 
    Infection Efficacy gives us a vaccine's efficacy at stopping transmission of the virus from one person to another. By definition, 1-'Infection Efficacy' will give us the Breakthrough Infection, which is % vaccinated people who get COVID-19 after exposed to the the SARS-CoV-2 virus.
    """)
    world["Alpha Breakthrough Infection"] = 100 - \
        world['Alpha Infection Efficacy']
    world["Delta Breakthrough Infection"] = 100 - \
        world['Delta Infection Efficacy']
    world['Omicron Breakthrough Infection'] = 100 - \
        world['Omicron Infection Efficacy']

    st.markdown("""
    **Third**, we will multiply **'% People Fully Vaccinated'** with **'Infection Efficacy'**.
    - Multiplying '% People Fully Vaccinated' with 'Alpha Infection Efficacy' will result in **'Alpha Protection'**, which gives us an idea of % people that are protected from Alpha Infection because they are fully vacinnated.
    - Multiplying '% People Fully Vaccinated' with 'Delta Infection Efficacy' will give 'Delta Protection'.
    - Multiplying '% People Fully Vaccinated' with 'Omicron Infection Efficacy' will give 'Omicron Protection'.""")
    world["Alpha Protection"] = world["% People Fully Vaccinated"] * \
        world['Alpha Infection Efficacy']/100
    world['Delta Protection'] = world["% People Fully Vaccinated"] * \
        world['Delta Infection Efficacy']/100
    world["Omicron Protection"] = world["% People Fully Vaccinated"] * \
        world["Omicron Infection Efficacy"]/100

    st.markdown("""
    **Fourth**, we can compute the **infection rate** by adding up unvaccinated people and breakthrough infection:
    - % People Not Fully Vaccinated can be calculated by subtracting % People Fully Vaccinated from 1; 
    - Before adding up, we need to modify the Breakthrough Infection by multiplying Breakthrough Infection by % People Fully Vaccinated, which yields % People who are susceptible to infection even though they are vaccinated;
    - Adding up modified Breakthrough Infection and % People Not Fully Vaccinated will result in the infection rate, % People that are susceptible to infection.
    """)
    st.markdown("""**Infection rate** can be calculated by subtracting protection from 1. Assume that unvaccinated people are susceptible to infection.
    - 100-'Alpha Protection' will result in 'Alpha Breakthrough Infection', % people that are not protected from alpha infection.
    - 100-'Delta Protection' will give 'Delta Breakthrough Infection'.
    - 100-'Omicron Protection' will give 'Omicron Breakthrough Infection'.
    """)
    world["Alpha Infection"] = 100-world['Alpha Protection']
    world["Delta Infection"] = 100-world['Delta Protection']
    world['Omicron Infection'] = 100-world['Omicron Protection']

    with st.expander("Click here to see the raw breakthrough infection data"):
        st.caption("Table 1: Breakthrough Infection Dataset")
        st.dataframe(world[['name', 'pop_est', '% People Fully Vaccinated',
                            "Alpha Breakthrough Infection", "Delta Breakthrough Infection", 'Omicron Breakthrough Infection',
                            "Alpha Protection", 'Delta Protection', 'Omicron Protection',
                            "Alpha Infection", "Delta Infection", 'Omicron Infection'
                            ]])

    world_notnull = world[world['Omicron Protection'].notnull()][['name', 'pop_est', '% People Fully Vaccinated', '% People Vaccinated',
                                                                  "Alpha Protection", 'Delta Protection', 'Omicron Protection',
                                                                  "Alpha Breakthrough Infection", "Delta Breakthrough Infection", 'Omicron Breakthrough Infection',
                                                                  "Alpha Infection", "Delta Infection", 'Omicron Infection'
                                                                  ]]
    st.write("**Fourth**, let us drop rows that contain null values for Protection and Breakthrough Infection columns.")
    st.dataframe(world_notnull)


with tab3:
    st.subheader("Visualize Breakthrough Infection")
    # world_notnull1 = world_notnull.sort_values(
    #     by=["% People Fully Vaccinated"])
    # fig1 = go.Figure()
    # fig1.add_trace(go.Bar(name="% People Fully Vaccinated", y=world_notnull1.name,
    #                x=world_notnull1["% People Fully Vaccinated"], orientation='h'))
    # fig1.update_layout(title="% People Fully Vaccinated")
    # st.plotly_chart(fig1)

    world_notnull = world_notnull.sort_values(
        by=['Alpha Breakthrough Infection'])

    selected_countries = st.multiselect(
        'Add country', list(world_notnull.name),
        ['Canada', 'United States of America', 'Ukraine', 'South Africa',])
    world_display1 = world_notnull[world_notnull['name'].isin(
        selected_countries)]
    fig = make_subplots(rows=1, cols=2, shared_yaxes=True,
                        subplot_titles=("% People Vaccinated", "Protection %")
                        )
    fig.append_trace(go.Bar(name="with 1 Plus Dose", y=world_display1.name, x=world_display1["% People Vaccinated"],
                            legendgrouptitle_text="% People Vaccinated", legendgroup="group", orientation='h'), 1, 1)
    fig.append_trace(go.Bar(name="Fully Vaccinated", y=world_display1.name, x=world_display1['% People Fully Vaccinated'],
                            legendgroup="group", orientation='h'), 1, 1)

    fig.append_trace(go.Bar(name="Omicron", y=world_display1.name, x=world_display1["Omicron Protection"],
                            legendgrouptitle_text="Protection %", legendgroup="group2", orientation='h'), 1, 2)
    fig.append_trace(go.Bar(name="Delta", y=world_display1.name,
                     x=world_display1["Delta Protection"], orientation='h'), 1, 2)
    fig.append_trace(go.Bar(name="Alpha", y=world_display1.name,
                     x=world_display1["Alpha Protection"], orientation='h'), 1, 2)
    st.plotly_chart(fig)
    fig1 = go.Figure()
    fig1 = make_subplots(rows=1, cols=2, shared_yaxes=True,
                         subplot_titles=(
                             "Breakthrough Infection %", "Infection %")
                         )
    fig1.append_trace(go.Bar(name="Alpha", y=world_display1.name, x=world_display1["Alpha Breakthrough Infection"],
                             legendgrouptitle_text="Breakthrough Infection %", legendgroup="group", orientation='h'), 1, 1)
    fig1.append_trace(go.Bar(name="Delta", y=world_display1.name, x=world_display1["Delta Breakthrough Infection"],
                             legendgroup="group", orientation='h'), 1, 1)
    fig1.append_trace(go.Bar(name="Omicron", y=world_display1.name, x=world_display1["Omicron Breakthrough Infection"],
                             legendgroup="group", orientation='h'), 1, 1)

    fig1.append_trace(go.Bar(name="Alpha", y=world_display1.name, x=world_display1["Alpha Infection"],
                             legendgrouptitle_text="Infection %", legendgroup="group2", orientation='h'), 1, 2)
    fig1.append_trace(go.Bar(name="Delta", y=world_display1.name, x=world_display1["Delta Infection"],
                             legendgroup="group2", orientation='h'), 1, 2)
    fig1.append_trace(go.Bar(name="Omicron", y=world_display1.name, x=world_display1["Omicron Infection"],
                             legendgroup="group2", orientation='h'), 1, 2)
    st.plotly_chart(fig1)
