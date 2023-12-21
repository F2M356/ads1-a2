import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the dataset
df = pd.read_csv("./API_19_DS2_en_csv_v2_5998250.csv", skiprows=4)

# G5 countries and relevant indicators
g5_countries = ["BRA", "CHN", "IND", "MEX", "ZAF"]
arable_land_indicator = "AG.LND.ARBL.ZS"
forest_area_indicator = "AG.LND.FRST.ZS"

# Filter data for G5 countries and relevant indicators
g5_arable_data = df[
    (df["Country Code"].isin(g5_countries))
    & (df["Indicator Code"] == arable_land_indicator)
]
g5_forest_data = df[
    (df["Country Code"].isin(g5_countries))
    & (df["Indicator Code"] == forest_area_indicator)
]


# Function to process and clean the data for plotting
def prepare_data_for_plotting(country_code, arable_data, forest_data):
    try:
        arable_series = (
            arable_data[arable_data["Country Code"] == country_code]
            .iloc[0, 4:]
            .dropna()
        )
        forest_series = (
            forest_data[forest_data["Country Code"] == country_code]
            .iloc[0, 4:]
            .dropna()
        )
        return arable_series, forest_series, True
    except IndexError:
        # Data not available for this country
        return None, None, False


# Function to align series and return common years with values
def align_series(series1, series2):
    common_years = series1.index.intersection(series2.index)
    return series1[common_years], series2[common_years], common_years


# Function to plot line chart
def time_series_line_plot(ax, country_code, country_name, arable_series, forest_series):
    # Aligning the series
    aligned_arable_series, aligned_forest_series, common_years = align_series(
        arable_series, forest_series
    )

    if common_years.empty:
        ax.text(0.5, 0.5, f"No common data available for {country_name}", ha="center")
        return

    # Convert common_years to integers
    common_years_int = common_years.astype(int)

    color = "tab:green"
    ax.set_ylabel("Arable Land (% of land area)", color=color)
    ax.plot(
        common_years_int,
        aligned_arable_series,
        color=color,
        label="Arable Land (% of land area)",
    )
    ax.tick_params(axis="y", labelcolor=color)

    ax2 = ax.twinx()
    color = "tab:brown"
    ax2.set_ylabel("Forest Area (% of land area)", color=color)
    ax2.plot(
        common_years_int,
        aligned_forest_series,
        color=color,
        label="Forest Area (% of land area)",
    )
    ax2.tick_params(axis="y", labelcolor=color)

    ax.set_title(f"Arable Land vs Forest Area for {country_name}")

    # Setting x-axis to show every 10 years
    ax.set_xticks(range(common_years_int.min(), common_years_int.max() + 1, 10))


# Line plot (subplot grid)
fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(18, 12))
axes = axes.flatten()

for i, country_code in enumerate(g5_countries):
    country_name = df[df["Country Code"] == country_code]["Country Name"].iloc[0]
    arable_series, forest_series, data_available = prepare_data_for_plotting(
        country_code, g5_arable_data, g5_forest_data
    )
    if data_available:
        time_series_line_plot(
            axes[i], country_code, country_name, arable_series, forest_series
        )
    else:
        axes[i].text(
            0.5,
            0.5,
            f"Data not available for {country_name} ({country_code})",
            ha="center",
        )

# Remove the unused subplot
axes[-1].axis("off")

plt.tight_layout()
plt.show()


# Function to get the latest available data for each country
def get_latest_data(arable_series, forest_series):
    latest_year = arable_series.last_valid_index()
    latest_arable_data = arable_series[latest_year]
    latest_forest_data = forest_series[latest_year]
    return latest_year, latest_arable_data, latest_forest_data


# Bar chart
countries = []
arable_data = []
forest_data = []

for country_code in g5_countries:
    country_name = df[df["Country Code"] == country_code]["Country Name"].iloc[0]
    arable_series, forest_series, data_available = prepare_data_for_plotting(
        country_code, g5_arable_data, g5_forest_data
    )
    if data_available:
        latest_year, latest_arable, latest_forest = get_latest_data(
            arable_series, forest_series
        )
        countries.append(country_name)
        arable_data.append(latest_arable)
        forest_data.append(latest_forest)

fig, ax = plt.subplots(figsize=(12, 6))
bar_width = 0.35
index = np.arange(len(countries))

bar1 = ax.bar(
    index,
    arable_data,
    bar_width,
    label="Arable Land (% of land area)",
    color="tab:green",
)
bar2 = ax.bar(
    index + bar_width,
    forest_data,
    bar_width,
    label="Forest Area (% of land area)",
    color="tab:brown",
)

ax.set_xlabel("Country")
ax.set_ylabel("Percentage of Land Area")
ax.set_title("Arable Land vs Forest Area for G5 Countries in the Latest Available Year")
ax.set_xticks(index + bar_width / 2)
ax.set_xticklabels(countries)
ax.legend()

plt.show()
