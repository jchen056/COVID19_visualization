import streamlit as st

st.title("Introduction")
st.sidebar.markdown("Home")

st.markdown('''COVID-19 vaccines help protect against severe illness, hospitalization, and death. Even though people who are vaccinated may still get COVID-19, they are much less likely to experience severe symptoms than people who are unvaccinated. The scenario in which people who are vaccinated get COVID-19 is referred to as a **“vaccine breakthrough infection.”**
In this post, we are going to examine the breakthrough Covid-19 infection.''')

st.subheader("Datasets")
st.markdown("""
Before we get started, let us review the datasets provided by Professor Majumder.
1. **Covid-19 Vaccine Efficacy**: vaccine efficacy data for variants of Covid-19; https://www.healthdata.org/covid/covid-19-vaccine-efficacy-summary 
2. **owid-covid-data-ALL-COUNTRIES**: a gigantic file with a size of 54.4 MB, recording information about population, cases, deaths, vaccination, and etc for different countries on a daily basis; https://ourworldindata.org/covid-vaccinations
3. **vaccination-data-WHO-12-28-2022-NO-DETAILS for-vaciinetype-date**: contains information about vaccines used and the number of people vaccinated for different countries in the world
4. **vaccinations-by-manufacturer-with-vaccine-efficacy-KM**: contains total vaccinations for each vaccine type in different counties in the world""")

st.subheader("Resources")
st.markdown('''Here are some additional datasets and visuals from which my project draws inspiration.
- Our World in Data: https://ourworldindata.org/covid-vaccinations 
- COVID Data Tracker: https://covid.cdc.gov/covid-data-tracker/#global-vaccinations 
- Vaccination by Manufacturer: https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations-by-manufacturer.csv
- Global Vaccination Data: https://github.com/owid/covid-19-data/tree/master/public/data/vaccinations
''')
