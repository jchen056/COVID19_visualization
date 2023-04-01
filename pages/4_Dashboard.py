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
                  )

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

st.subheader("What % of the population has been vaccinated?")
with st.expander("Click here to view % People Vaccinated on a global map:"):
    st_folium(m)
options = sorted(list(df_n.name))
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

st.subheader("How many vaccine doses have been administered in each country?")
df_t = pd.read_csv(
    "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations-by-manufacturer.csv")
change_country = sorted(list(set(list(df_t['location']))))
country_opt = st.selectbox("Change Country", change_country)
df_gb = df_t[df_t["location"] == country_opt]
n_dates = len(set(list(df_gb["date"])))
n_vaccines = len(set(list(df_gb["vaccine"])))
df_gb_modified = pd.DataFrame(np.zeros((n_dates*n_vaccines, 4)),
                              columns=['location', 'date', 'vaccine', 'total_vaccinations'])
df_gb_modified['location'] = country_opt

dates = []
for j in sorted(set(list(df_gb["date"]))):
    for i in range(n_vaccines):
        dates.append(j)
df_gb_modified["date"] = dates
vaccines = []
for i in range(n_dates):
    for j in set(list(df_gb["vaccine"])):
        vaccines.append(j)
df_gb_modified['vaccine'] = vaccines
for i in range(len(df_gb_modified)):
    temp_arr = df_gb[(df_gb['date'] == df_gb_modified.loc[i, 'date']) & (
        df_gb['vaccine'] == df_gb_modified.loc[i, 'vaccine'])]["total_vaccinations"].values
    if len(temp_arr) != 0:
        df_gb_modified.loc[i, 'total_vaccinations'] = temp_arr[0]
sorted_dates = sorted(list(set(list(df_gb["date"]))))
for i in range(6, len(df_gb_modified)):
    if df_gb_modified.loc[i, "total_vaccinations"] == 0:
        prev_date = sorted_dates[sorted_dates.index(
            df_gb_modified.loc[i, "date"])-1]
        df_gb_modified.loc[i, "total_vaccinations"] = df_gb_modified[(df_gb_modified['vaccine'] == df_gb_modified.loc[i, "vaccine"]) & (
            df_gb_modified['date'] == prev_date)]["total_vaccinations"].values[0]

fig = go.Figure()
vacs = df_gb_modified.tail(n_vaccines).sort_values(
    by="total_vaccinations")["vaccine"].values
for i in vacs:
    fig.add_trace(go.Scatter(name=i, x=df_gb_modified[df_gb_modified["vaccine"] == i]["date"],
                             y=df_gb_modified[df_gb_modified["vaccine"]
                                              == i]["total_vaccinations"],
                             stackgroup="one", mode='lines',))
fig.update_layout(
    title="COVID-19 vaccine doses administered by manufacturer, "+country_opt)
st.plotly_chart(fig)
st.caption("Source: https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations-by-manufacturer.csv")

st.subheader(
    "What % of the Population is Susceptible to Infection and Protected from Infection?")
df_infection = geopandas.read_file("data/infection.shp")
with st.expander("Click here to view infection and protection rate on a global map"):
    tb1, tb2 = st.tabs(["Infection", "Protection"])
    with tb1:
        m1 = df_infection.explore(column='Omicron Infection', cmap="YlGn",
                                  tiles="CartoDB positron", tooltip='name',
                                  popup=['name', 'pop_est',
                                         "Persons_Fully_Vaccinated",
                                         'Alpha Infection', 'Delta Infection', 'Omicron Infection'
                                         ],)
        st_folium(m1)
    with tb2:
        m2 = df_infection.explore(column='Omicron Protection', cmap="YlGn",
                                  tiles="CartoDB positron", tooltip='name',
                                  popup=['name', 'pop_est',
                                         "Persons_Fully_Vaccinated",
                                         'Alpha Protection', 'Delta Protection', 'Omicron Protection'
                                         ],)
        st_folium(m2)
    st.caption("Grey area has no data.")
df_infection_notnull = df_infection[df_infection['Alpha Protection'].notnull()]
infection_countries = sorted(list(df_infection_notnull['name']))
infection_cnt_select = st.multiselect('Add Country', infection_countries, [
                                      'Argentina', 'South Africa', 'Ukraine', 'Canada', 'Germany', 'United States of America'])
df_infection_notnull = df_infection_notnull[df_infection_notnull['name'].isin(
    infection_cnt_select)]
fig1 = make_subplots(rows=6, cols=1,
                     specs=[[{"rowspan": 2}], [None],
                            [{"rowspan": 2}], [None],
                            [{"rowspan": 2}], [None]],
                     shared_xaxes=True,
                     subplot_titles=("Alpha Variant", "Delta Variant", "Omicron Variant"))
fig1.append_trace(go.Bar(name="Alpha Infection",
                         legendgrouptitle_text="Infection", legendgroup="infection",
                         x=df_infection_notnull['name'], y=df_infection_notnull['Alpha Infection']), 1, 1)
fig1.append_trace(go.Bar(name="Alpha Protection",
                         legendgrouptitle_text="Protection", legendgroup="protection",
                         x=df_infection_notnull['name'], y=df_infection_notnull['Alpha Protection']), 1, 1)

fig1.append_trace(go.Bar(name="Delta Infection",
                         legendgroup="infection",
                         x=df_infection_notnull['name'], y=df_infection_notnull['Delta Infection']), 3, 1)
fig1.append_trace(go.Bar(name="Delta Protection",
                         legendgroup="protection",
                         x=df_infection_notnull['name'], y=df_infection_notnull['Delta Protection']), 3, 1)

fig1.append_trace(go.Bar(name="Omicron Infection",
                         legendgroup="infection",
                         x=df_infection_notnull['name'], y=df_infection_notnull['Omicron Infection']), 5, 1)
fig1.append_trace(go.Bar(name="Omicron Protection",
                         legendgroup="protection",
                         x=df_infection_notnull['name'], y=df_infection_notnull['Omicron Protection']), 5, 1)
fig1.update_layout(
    title="% Population Susceptible to Infection and Protected from Infection", barmode="stack")
st.plotly_chart(fig1)
