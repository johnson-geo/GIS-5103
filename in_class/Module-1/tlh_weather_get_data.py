# import an external package that we will need; the convention is to put all imports at the
# beginning of the file
import pandas as pd




#####################################################
### Read data from NCEI directly into a dataframe ###
#####################################################

# split up various pieces of the URL so it's easier to keep track of
weather_url_dataset = "daily-summaries"
weather_url_vars = "PRCP,SNWD,SNOW,TAVG,TMAX,TMIN,AWND,WDF2,WDF5,WSF2,WSF5,PGTM,WT01,WT02,WT08,WT03"
weather_url_station = "USW00093805"
weather_url_start_date = "2018-09-01"
weather_url_end_date = "2019-08-31"
weather_url_units = "standard"


# concatenate all the pieces into the final URL
weather_url = "https://www.ncei.noaa.gov/access/services/data/v1?" + \
              "dataset=" + weather_url_dataset + \
              "&dataTypes=" + weather_url_vars + \
              "&stations=" + weather_url_station + \
              "&startDate=" + weather_url_start_date + \
              "&endDate=" + weather_url_end_date + \
              "&units=" + weather_url_units
print(weather_url)


# make the call to the internet to pull the data, then write to hard drive
raw = pd.read_csv(weather_url)
raw.to_csv("tlh_weather_data.csv", index=False)





