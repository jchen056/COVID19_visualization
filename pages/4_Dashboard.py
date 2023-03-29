import streamlit as st
import pandas as pd
import numpy as np
import geopandas
import plotly.express as px
import plotly.graph_objects as go
from streamlit_folium import st_folium
from plotly.subplots import make_subplots


df_vaccine = pd.read_excel(
    'data/vaccination-data-WHO-12-28-2022-NO-DETAILS for-vaciinetype-date.xlsx')
df_vaccine = df_vaccine[df_vaccine["COUNTRY"] != "Eritrea"]
total_dose = round(np.sum(df_vaccine["TOTAL_VACCINATIONS"])/1000000000, 2)

world = geopandas.read_file(
    geopandas.datasets.get_path('naturalearth_lowres'))
world.rename(columns={'iso_a3': 'ISO3'}, inplace=True)
world["Total_Vaccinations"] = np.nan
world['vaccines'] = np.nan
world["Persons_Fully_Vaccinated"] = np.nan
world["persons_vaccinated"] = np.nan

for i in range(world.shape[0]):
    iso_code = world.loc[i]["ISO3"]
    if iso_code in list(df_vaccine["ISO3"]):
        world.at[i, "Total_Vaccinations"] = df_vaccine[df_vaccine["ISO3"]
                                                       == iso_code].iloc[0]["TOTAL_VACCINATIONS"]
        world.at[i, "vaccines"] = df_vaccine[df_vaccine["ISO3"]
                                             == iso_code].iloc[0]["VACCINES_USED"]
        world.at[i, "Persons_Fully_Vaccinated"] = df_vaccine[df_vaccine["ISO3"]
                                                             == iso_code].iloc[0]["PERSONS_FULLY_VACCINATED"]
        world.at[i, "persons_vaccinated"] = df_vaccine[df_vaccine["ISO3"]
                                                       == iso_code].iloc[0]["PERSONS_VACCINATED_1PLUS_DOSE"]
world["% People Vaccinated"] = world["Persons_Fully_Vaccinated"] / \
    world['pop_est']*100
world["% People Fully Vaccinated"] = world["persons_vaccinated"] / \
    world["pop_est"]*100
world = world[world.name != 'Antarctica']
m = world.explore(column="% People Vaccinated", cmap="YlGn",
                  tiles="CartoDB positron", tooltip='name',
                  popup=['name', 'pop_est',
                         "% People Vaccinated", "persons_vaccinated",
                         '% People Fully Vaccinated', "Persons_Fully_Vaccinated"],
                  width="100%", height=400)

# world_notnull = world[world["Total_Vaccinations"].notnull()]
# total_pop = np.sum(world_notnull["pop_est"])
# perc_fully_vacc = round(
#     world_notnull["Persons_Fully_Vaccinated"].sum()/total_pop*100, 2)
# perc_ppl_vac = round(
#     world_notnull["persons_vaccinated"].sum()/total_pop*100, 2)
df_n = pd.read_csv("data/world_dataset.csv")
df_n = df_n[df_n["Total_Vaccinations"].notnull()]
total_pop = np.sum(df_n["pop_est"])
perc_fully_vacc = round(
    np.sum(df_n["Persons_Fully_Vaccinated"])/total_pop*100, 2)
perc_ppl_vac = round(np.sum(df_n["persons_vaccinated"])/total_pop*100, 2)

col1, col2, col3 = st.columns(3)
col1.metric("Total Vaccinations", value=str(total_dose)+" billion")
col2.metric("% People Vaccinated w/ 1 Plus Dose", value=str(perc_ppl_vac)+"%")
col3.metric("% People Fully Vaccinated", value=str(perc_fully_vacc)+"%")
st.caption("The data is no longer being updated. Data is as of December 28, 2022.")
st_folium(m)
options = list(df_n.name)
options_countries = st.multiselect(
    'Add country',
    options,
    ['India', 'China', 'Brazil', 'Russia', 'United States of America'])
df_n_countries = df_n[df_n["name"].isin(options_countries)].sort_values(
    by=["% People Vaccinated", "% People Fully Vaccinated"], ascending=False)
fig = make_subplots(rows=1, cols=2, shared_yaxes=True,
                    subplot_titles=("% People Vaccinated", "Number of People Vaccianted",))
fig.append_trace(go.Bar(x=df_n_countries["% People Vaccinated"], y=df_n_countries.name, orientation='h', name="w/ 1 Plus Dose",
                        legendgrouptitle_text="% People Vaccinated:", legendgroup="group"), 1, 1)
fig.append_trace(go.Bar(x=df_n_countries["% People Fully Vaccinated"], y=df_n_countries.name, orientation='h', name="Fully Vaccinated",
                        legendgroup="group1"), 1, 1)

fig.append_trace(go.Bar(x=df_n_countries["persons_vaccinated"], y=df_n_countries.name, orientation='h', name="Fully",
                        legendgrouptitle_text="Number of People Vaccinated:",
                        legendgroup="group2"), 1, 2)
fig.append_trace(go.Bar(x=df_n_countries["Persons_Fully_Vaccinated"], y=df_n_countries.name,
                 orientation='h', name="w/ 1 Plus Dose", legendgroup="group3"), 1, 2)

fig.update_layout(barmode='overlay')
st.plotly_chart(fig)
