import streamlit as st
import pandas as pd
import numpy as np
import geopandas
import plotly.express as px
import matplotlib.pyplot as plt
from PIL import Image
import streamlit.components.v1 as components
import plotly.graph_objects as go
from streamlit_folium import st_folium


# st.title("Breakthrough Covid-19 Infection")
st.title("Vaccine Distribution")
st.sidebar.markdown("Vaccine Distribution")
st.markdown('''In this section, we will examine the vaccination dataset and come up with some visuals to understand the vaccine distribution.''')

tb1, tb2, tb3 = st.tabs(
    ["Vaccination Dataset", "World Dataset", "Vaccine Distribution"])
with tb1:
    # load vaccination data and clean it
    df_vaccine = pd.read_excel(
        'data/vaccination-data-WHO-12-28-2022-NO-DETAILS for-vaciinetype-date.xlsx')
    st.subheader("Vaccination Dataset Manipulation")
    with st.expander("Click here to view the raw vaccination dataset"):
        st.caption("Table 1: Vaccination Dataset")
        st.dataframe(df_vaccine)
        st.caption(
            "Source: Provided by Professor Majumder, **vaccinations-by-manufacturer-with-vaccine-efficacy-KM**")
    st.write("**First**, let us take a look at the columns we have for the dataframe:",
             df_vaccine.columns)
    st.write("Columns of our interest include **COUNTRY, ISO3, WHO_REGION, PERSONS_VACCINATED_1PLUS_DOSE, PERSONS_FULLY_VACCINATED, and VACCINES_USED**.")
    st.write("**Second**, let us check whether we have null data:",
             df_vaccine.isnull().sum())
    st.write("As we can see, there is a row where TOTAL_VACCINATIONS is null. We need to drop that row because it does not have data for PERSONS_VACCINATED_1PLUS_DOSE and PERSONS_FULLY_VACCINATED.")
    st.dataframe(df_vaccine[df_vaccine["COUNTRY"] == "Eritrea"])
    st.write(
        "**Third**, let us drop unnecessary columns so that our dataset will be easier to handle.")
    with st.expander("Click here to view cleaned vaccination dataset"):
        st.caption("Table 2: Cleaned Vaccination Dataset")
        df_vaccine_displayed = df_vaccine[['COUNTRY', 'ISO3', 'WHO_REGION',
                                           'PERSONS_VACCINATED_1PLUS_DOSE', 'PERSONS_FULLY_VACCINATED', 'VACCINES_USED']]
        st.dataframe(df_vaccine_displayed)

with tb2:
    st.subheader("Combining Vaccination Dataset with World Dataset")
    # load the dataset from geopandas
    world = geopandas.read_file(
        geopandas.datasets.get_path('naturalearth_lowres'))
    world.rename(columns={'iso_a3': 'ISO3'}, inplace=True)
    world['gdp_per_cap'] = world.gdp_md_est / world.pop_est
    st.markdown('''
    Instead of using the population data provided my Professor Majumder, we will be using the population data from a dataset found in GeoPandas because
    1. The dataset including population data provided by Professor Majumder takes some time to load while the dataset found in GeoPandas loads really quickly;
    2. GeoPandas dataset includes some columns that are necessary for plotting a map.
    ''')
    with st.expander("Click here to view Country GeoDataFrame"):
        st.caption("Table 3: Country GeoDataFrame")
        world
        st.caption(
            "Source: https://geopandas.org/en/stable/docs/user_guide/mapping.html")

    world["Total_Vaccinations"] = np.nan
    world['vaccines'] = np.nan
    world["Persons_Fully_Vaccinated"] = np.nan
    world["Total_Vaccinations_Per100"] = np.nan
    world["Persons_Fully_Vaccinated_Per100"] = np.nan
    world["persons_vaccinated"] = np.nan
    world["persons_vaccinated_per100"] = np.nan

    for i in range(world.shape[0]):
        iso_code = world.loc[i]["ISO3"]
        if iso_code in list(df_vaccine["ISO3"]):
            world.at[i, "Total_Vaccinations"] = df_vaccine[df_vaccine["ISO3"]
                                                           == iso_code].iloc[0]["TOTAL_VACCINATIONS"]
            world.at[i, "vaccines"] = df_vaccine[df_vaccine["ISO3"]
                                                 == iso_code].iloc[0]["VACCINES_USED"]
            world.at[i, "Persons_Fully_Vaccinated"] = df_vaccine[df_vaccine["ISO3"]
                                                                 == iso_code].iloc[0]["PERSONS_FULLY_VACCINATED"]
            world.at[i, "Total_Vaccinations_Per100"] = df_vaccine[df_vaccine["ISO3"]
                                                                  == iso_code].iloc[0]["TOTAL_VACCINATIONS_PER100"]
            world.at[i, "Persons_Fully_Vaccinated_Per100"] = df_vaccine[df_vaccine["ISO3"]
                                                                        == iso_code].iloc[0]["PERSONS_FULLY_VACCINATED_PER100"]
            world.at[i, "persons_vaccinated"] = df_vaccine[df_vaccine["ISO3"]
                                                           == iso_code].iloc[0]["PERSONS_VACCINATED_1PLUS_DOSE"]
            world.at[i, "persons_vaccinated_per100"] = df_vaccine[df_vaccine["ISO3"]
                                                                  == iso_code].iloc[0]["PERSONS_VACCINATED_1PLUS_DOSE_PER100"]
    st.markdown('''
    Let us combine Vaccination Dataset and World Dataset by using **inner join**.
    After inner join, we will drop rows with null values in 'Persons_Fully_Vaccinated' column. ''')
    world = world[(world.pop_est > 0) & (world.name != "Antarctica")]
    world = world[world.Persons_Fully_Vaccinated.notnull()]
    st.caption("Table 4: Vaccination Dataset and World Dataset Combined")
    world
    st.markdown('''
    After that, we can compute (1)'% People Fully Vaccinated' by dividing 'Persons_Fully_Vaccinated' By 'pop_est' and (2)'% People Vaccinated' by
     dividing 'persons_vaccinated' by 'pop_est'. ''')
    world["% People Fully Vaccinated"] = world['Persons_Fully_Vaccinated'] / \
        world['pop_est']*100
    world["% People Vaccinated"] = world['persons_vaccinated'] / \
        world['pop_est']*100
    world.to_csv("data/world_dataset.csv")
    world1 = world.sort_values(
        by=["% People Fully Vaccinated", "% People Vaccinated"], ascending=False)
    with st.expander("Click here to view % People Fully Vaccinated and % People Vaccinated with 1 Plus Dose Data"):
        world1[["name", "continent", "ISO3",
                "% People Fully Vaccinated", "% People Vaccinated"]]

    st.subheader("Breakdown of People Vaccinated")
    st.write('''The following charts show the breakdown of people vaccinated, between those who are fully vaccinated and those who are vaccinated with 1 plus doese.''')
    tab_top, tab_bottom = st.tabs(
        ["Top 15 Countries", "Bottom 15 Countries"])
    world1 = world.sort_values(
        by=["% People Vaccinated", "% People Fully Vaccinated"], ascending=False)
    with tab_top:
        fig = go.Figure(data=[
            go.Bar(name="% People Vaccinated",
                   x=world1["name"][0:15], y=world1["% People Vaccinated"][0:15]),
            go.Bar(name="% People Fully Vaccinated",
                   x=world1["name"][0:15], y=world1["% People Fully Vaccinated"][0:15])
        ])
        fig.update_layout(
            title="The Breakdown of People Vaccinated", barmode='overlay')
        st.plotly_chart(fig, theme=None, use_container_width=True)
    with tab_bottom:
        fig = go.Figure(data=[
            go.Bar(name="% People Vaccinated",
                   x=world1["name"][-15:-1], y=world1["% People Vaccinated"][-15:-1]),
            go.Bar(name="% People Fully Vaccinated",
                   x=world1["name"][-15:-1], y=world1["% People Fully Vaccinated"][-15:-1])
        ])
        fig.update_layout(
            title="The Breakdown of People Vaccinated", barmode='overlay')
        st.plotly_chart(fig, theme=None, use_container_width=True)
    df_Africa = world1[world1["continent"] == 'Africa']
    df_Asia = world1[world1["continent"] == 'Asia']
    df_Europe = world1[world1["continent"] == 'Europe']
    df_NA = world1[world1["continent"] == 'North America']
    df_SA = world1[world1["continent"] == 'South America']
    df_Oceania = world1[world1["continent"] == 'Oceania']
    fig = go.Figure()
    fig.add_trace(
        go.Bar(name="Africa", x=df_Africa["name"][0:5], y=df_Africa["% People Vaccinated"][0:5]))
    fig.add_trace(go.Bar(
        name="Asia", x=df_Asia["name"][0:5], y=df_Asia["% People Vaccinated"][0:5]))
    fig.add_trace(go.Bar(
        name="Europe", x=df_Europe["name"][0:5], y=df_Europe["% People Vaccinated"][0:5]))
    fig.add_trace(go.Bar(name="North America",
                  x=df_NA["name"][0:5], y=df_NA["% People Vaccinated"][0:5]))
    fig.add_trace(go.Bar(name="South America",
                  x=df_SA["name"][0:5], y=df_SA["% People Vaccinated"][0:5]))
    fig.add_trace(go.Bar(
        name="Oceania", x=df_Oceania["name"][0:5], y=df_Oceania["% People Vaccinated"][0:5]))
    fig.update_layout(title="% People Vaccinated by Continents")
    st.plotly_chart(fig)

    m = world.explore(
        column="% People Fully Vaccinated",
        legend=True,  # show legend
        tooltip=["name"],  # show value in tooltip (on hover)
        popup=["name", "Persons_Fully_Vaccinated", "% People Fully Vaccinated",
               "persons_vaccinated", "% People Vaccinated"],  # show all values in popup (on click)
    )
    m.save("iframe/Vaccine_Dist_PPL_Vacc.html")

    st.subheader("Additional Notes: All about Population")
    st.markdown("""
    The vaccination figures on this page may look different from the ones reported by governments. 
    Most often it is not because of the numerator (number of people vaccinated) but instead because of the denominator (**number of people in the population**). 
    """)


with tb3:
    st.subheader("Vaccination Rates Are Low in Africa")
    st.caption(
        'These maps are no longer being updated. Data is as of December 28, 2022.')
    tab1, tab3, tab2 = st.tabs(
        ["Geographical Scatter Plot", "Interactive Folium Map", "Static Maps"])
    with tab1:
        fig = px.scatter_geo(world, locations="ISO3", hover_name="name",
                             hover_data=["pop_est", "Persons_Fully_Vaccinated", "% People Fully Vaccinated",
                                         "persons_vaccinated", "% People Vaccinated"],
                             color="% People Fully Vaccinated",
                             size='pop_est',
                             projection="natural earth")
        fig.update_layout(
            title='% People Fully Vaccinated',
        )
        st.plotly_chart(fig, theme=None, use_container_width=True)
        st.caption("The size of the bubble gives the information about pop_est: a bigger bubble indicates a larger population. The color of the bubble gives the information of % people fully vaccinated. Hover over the bubble to see vaccination info for each country. ")

    with tab3:
        st_folium(m)
    with tab2:
        with st.container():
            col1, col2, col3 = st.columns(3)
            with col1:
                fig, ax = plt.subplots(1, 1)
                world.plot(column="pop_est", legend=True, ax=ax,
                           legend_kwds={'label': "Population Estimate by Country",
                                        'orientation': "horizontal"}, cmap='YlOrRd')
                ax.set_axis_off()
                st.pyplot(fig)
            with col2:
                fig, ax = plt.subplots(1, 1)
                world.plot(column="Total_Vaccinations", ax=ax, legend=True,
                           legend_kwds={'label': "Total Vacccination by Country",
                                        'orientation': "horizontal"}, cmap="YlOrRd")
                ax.set_axis_off()
                st.pyplot(fig)
            with col3:
                fig, ax = plt.subplots(1, 1)
                world.plot(column="Persons_Fully_Vaccinated", legend=True, ax=ax,
                           legend_kwds={'label': "Persons Fully Vaccinated by Country",
                                        'orientation': "horizontal"}, cmap='YlOrRd')
                ax.set_axis_off()
                st.pyplot(fig)

            col4, col5, col6 = st.columns(3)
            with col4:
                fig, ax = plt.subplots(1, 1)
                world.plot(column="gdp_per_cap", legend=True, ax=ax,
                           legend_kwds={'label': "GDP per capita by Country",
                                        'orientation': "horizontal"}, cmap='YlOrRd')
                ax.set_axis_off()
                st.pyplot(fig)
            with col5:
                fig, ax = plt.subplots(1, 1)
                world.plot(column="Total_Vaccinations_Per100", ax=ax, legend=True,
                           legend_kwds={'label': "Total Vacccination Per100 by Country",
                                        'orientation': "horizontal"}, cmap="YlOrRd")
                ax.set_axis_off()
                st.pyplot(fig)
            with col6:
                fig, ax = plt.subplots(1, 1)
                world.plot(column="Persons_Fully_Vaccinated_Per100", legend=True, ax=ax,
                           legend_kwds={'label': "Persons Fully Vaccinated Per100 by Country",
                                        'orientation': "horizontal"}, cmap='OrRd')
                ax.set_axis_off()
                st.pyplot(fig)
    st.write(
        "**Food for thought**: Why do Covid-19 vaccination rates remain low in most countries in Africa?")

    st.subheader("Where Are Vaccines Administered Distributed?")
    st.caption(
        'These maps are no longer being updated. Data is as of December 28, 2022.')

    def contains_vaccine_specific(s, vac):
        if type(s) == float:
            return 0
        else:
            if vac in s:
                return 1  # 1 means yes and 0 means no
            else:
                return 0

    vaccines_of_interest = ['AstraZeneca', 'Pfizer', 'Moderna',
                            'BBIBP', 'Gamaleya', 'Sinovac', 'Janssen', 'Bharat', 'Novavax']
    for i in vaccines_of_interest:
        world[i] = world["vaccines"].apply(
            lambda x: contains_vaccine_specific(x, i))
    df_AstraZeneca1 = world[world["AstraZeneca"] == 1]
    df_Pfizer1 = world[world["Pfizer"] == 1]
    df_Moderna1 = world[world["Moderna"] == 1]
    df_BBIBP1 = world[world["BBIBP"] == 1]
    df_Gamaleya1 = world[world["Gamaleya"] == 1]
    df_Sinovac1 = world[world["Sinovac"] == 1]
    df_JJ1 = world[world["Janssen"] == 1]
    df_Bharat1 = world[world["Bharat"] == 1]
    df_Novavax1 = world[world["Novavax"] == 1]
    df_AstraZeneca1 = df_AstraZeneca1[['pop_est', 'continent', 'name', 'ISO3', 'gdp_md_est', 'geometry',
                                       'vaccines', 'Total_Vaccinations', 'Persons_Fully_Vaccinated', "Persons_Fully_Vaccinated_Per100", "persons_vaccinated_per100"]]
    df_AstraZeneca1["vaccine"] = "AstraZeneca"

    df_Pfizer1 = df_Pfizer1[['pop_est', 'continent', 'name', 'ISO3', 'gdp_md_est', 'geometry',
                            'vaccines', 'Total_Vaccinations', 'Persons_Fully_Vaccinated', "Persons_Fully_Vaccinated_Per100", "persons_vaccinated_per100"]]
    df_Pfizer1["vaccine"] = "Pfizer"

    df_Moderna1 = df_Moderna1[['pop_est', 'continent', 'name', 'ISO3', 'gdp_md_est', 'geometry',
                               'vaccines', 'Total_Vaccinations', 'Persons_Fully_Vaccinated', "Persons_Fully_Vaccinated_Per100", "persons_vaccinated_per100"]]
    df_Moderna1["vaccine"] = "Moderna"

    df_BBIBP1 = df_BBIBP1[['pop_est', 'continent', 'name', 'ISO3', 'gdp_md_est', 'geometry',
                           'vaccines', 'Total_Vaccinations', 'Persons_Fully_Vaccinated', "Persons_Fully_Vaccinated_Per100", "persons_vaccinated_per100"]]
    df_BBIBP1["vaccine"] = "BBIBP"

    df_Gamaleya1 = df_Gamaleya1[['pop_est', 'continent', 'name', 'ISO3', 'gdp_md_est', 'geometry',
                                'vaccines', 'Total_Vaccinations', 'Persons_Fully_Vaccinated', "Persons_Fully_Vaccinated_Per100", "persons_vaccinated_per100"]]
    df_Gamaleya1["vaccine"] = "Gamaleya"

    df_Sinovac1 = df_Sinovac1[['pop_est', 'continent', 'name', 'ISO3', 'gdp_md_est', 'geometry',
                               'vaccines', 'Total_Vaccinations', 'Persons_Fully_Vaccinated', "Persons_Fully_Vaccinated_Per100", "persons_vaccinated_per100"]]
    df_Sinovac1["vaccine"] = "Sinovac"

    df_JJ1 = df_JJ1[['pop_est', 'continent', 'name', 'ISO3', 'gdp_md_est', 'geometry',
                    'vaccines', 'Total_Vaccinations', 'Persons_Fully_Vaccinated', "Persons_Fully_Vaccinated_Per100", "persons_vaccinated_per100"]]
    df_JJ1["vaccine"] = "Johnson & Johnson"

    df_Bharat1 = df_Bharat1[['pop_est', 'continent', 'name', 'ISO3', 'gdp_md_est', 'geometry',
                            'vaccines', 'Total_Vaccinations', 'Persons_Fully_Vaccinated', "Persons_Fully_Vaccinated_Per100", "persons_vaccinated_per100"]]
    df_Bharat1["vaccine"] = "Bharat"

    df_Novavax1 = df_Novavax1[['pop_est', 'continent', 'name', 'ISO3', 'gdp_md_est', 'geometry',
                               'vaccines', 'Total_Vaccinations', 'Persons_Fully_Vaccinated', "Persons_Fully_Vaccinated_Per100", "persons_vaccinated_per100"]]
    df_Novavax1["vaccine"] = "Novavax"
    df = pd.concat([df_AstraZeneca1, df_Pfizer1, df_Moderna1, df_BBIBP1,
                    df_Gamaleya1, df_Sinovac1, df_JJ1, df_Bharat1, df_Novavax1], axis=0)
    with st.container():
        tab1, tab2 = st.tabs(["Interactive Maps", "Static Maps"])
        with tab1:
            fig = px.scatter_geo(df, locations="ISO3",
                                 color="vaccine",
                                 hover_name="name",
                                 hover_data=[
                                     'name', 'pop_est', "Persons_Fully_Vaccinated_Per100", "persons_vaccinated_per100"],
                                 #                    size='Total_Vaccinations',
                                 animation_frame="vaccine",
                                 projection="natural earth")
            fig.update_layout(title="Vaccine Distribution",
                              #                   height=500, margin={"r":0,"t":0,"l":0,"b":0},
                              )
            st.plotly_chart(fig, theme="streamlit", use_container_width=True)
        with tab2:
            c1, c2, c3 = st.columns(3)
            with c1:
                ax = world.plot(color='lightgrey')
                ax.set_aspect('equal')
                ax.set_axis_off()
                ax.set_title("AstraZeneca")
                df_AstraZeneca1.plot(ax=ax, color="darkorange")
                plt.savefig('iframe/AstraZeneca.png')
                image1 = Image.open('iframe/AstraZeneca.png')
                st.image(image1, use_column_width='always',
                         caption="112 countries")
            with c2:
                ax = world.plot(color='lightgrey')
                ax.set_aspect('equal')
                ax.set_axis_off()
                ax.set_title("Pfizer")
                df_Pfizer1.plot(ax=ax, color="darkblue")
                plt.savefig('iframe/Pfizer.png')
                image1 = Image.open('iframe/Pfizer.png')
                st.image(image1, use_column_width='always',
                         caption="126 countries")
            with c3:
                ax = world.plot(color='lightgrey')
                ax.set_aspect('equal')
                ax.set_axis_off()
                ax.set_title("Moderna")
                df_Moderna1.plot(ax=ax, color="green")
                plt.savefig('iframe/Moderna.png')
                image1 = Image.open('iframe/Moderna.png')
                st.image(image1, use_column_width='always',
                         caption="100 countries")
            c4, c5, c6 = st.columns(3)
            with c4:
                ax = world.plot(color='lightgrey')
                ax.set_aspect('equal')
                ax.set_axis_off()
                ax.set_title("BBIBP")
                df_BBIBP1.plot(ax=ax, color="red")
                plt.savefig('iframe/BBIBP.png')
                image1 = Image.open('iframe/BBIBP.png')
                st.image(image1, use_column_width='always',
                         caption="88 countries")
            with c5:
                ax = world.plot(color='lightgrey')
                ax.set_aspect('equal')
                ax.set_axis_off()
                ax.set_title("Gamaleya")
                df_Gamaleya1.plot(ax=ax, color="gold")
                plt.savefig('iframe/Gamaleya.png')
                image1 = Image.open('iframe/Gamaleya.png')
                st.image(image1, use_column_width='always',
                         caption="64 countries")
            with c6:
                ax = world.plot(color='lightgrey')
                ax.set_aspect('equal')
                ax.set_axis_off()
                ax.set_title("Sinovac")
                df_Sinovac1.plot(ax=ax, color="deeppink")
                plt.savefig('iframe/Sinovac.png')
                image1 = Image.open('iframe/Sinovac.png')
                st.image(image1, use_column_width='always',
                         caption="62 countries")
            c7, c8, c9 = st.columns(3)
            with c7:
                ax = world.plot(color='lightgrey')
                ax.set_aspect('equal')
                ax.set_axis_off()
                ax.set_title("Johnson & Johnson")
                df_JJ1.plot(ax=ax, color="purple")
                plt.savefig('iframe/JJ.png')
                image1 = Image.open('iframe/JJ.png')
                st.image(image1, use_column_width='always',
                         caption="103 countries")
            with c8:
                ax = world.plot(color='lightgrey')
                ax.set_aspect('equal')
                ax.set_axis_off()
                ax.set_title("Bharat")
                df_Bharat1.plot(ax=ax, color="mediumturquoise")
                plt.savefig('iframe/Bharat.png')
                image1 = Image.open('iframe/Bharat.png')
                st.image(image1, use_column_width='always',
                         caption="30 countries")
            with c9:
                ax = world.plot(color='lightgrey')
                ax.set_aspect('equal')
                ax.set_axis_off()
                ax.set_title("Novavax")
                df_Novavax1.plot(ax=ax, color="dodgerblue")
                plt.savefig('iframe/Novavax.png')
                image1 = Image.open('iframe/Novavax.png')
                st.image(image1, use_column_width='always',
                         caption="28 countries")
