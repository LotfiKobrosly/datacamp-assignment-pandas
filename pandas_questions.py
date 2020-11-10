"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""
import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.DataFrame(pd.read_csv("./data/referendum.csv", sep=";"))
    regions = pd.DataFrame(pd.read_csv("./data/regions.csv"))
    departments = pd.DataFrame(pd.read_csv("./data/departments.csv"))
    # Column names
    # regions: id, code, name, slug
    # departments: id, region_code, code, name, slug
    # referendum: Department code, Department name, Town code,
    #             Town name, Registered, Abstentions, Null,
    #             Choice A, Choice B

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']

    Parameters
    ----------
    regions: pandas.DataFrame
        contains information about regions

    departments: pandas.DataFrame
        contains information about departments

    Returns
    -------
    df : pandas.DataFrame
        merged dataframes

    Raises
    ------
    None

    """
    df = pd.DataFrame({
        "code_reg": departments["region_code"],
        "name_reg": ["" for _ in range(departments.shape[0])],
        "code_dep": departments["code"],
        "name_dep": departments["name"]
    })
    for i, row in regions.iterrows():
        mask = df["code_reg"] == row["code"]
        df.loc[mask, "name_reg"] = row["name"]

    return df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.

    Parameters
    ----------
    referendum: pandas.DataFrame
        contains information about referendums in different departments

    regions_and_departments: pandas.DataFrame
        contains information about departments and their regions

    Returns
    -------
    df : pandas.DataFrame
        merged dataframes
    """
    # Removing DOM-TOM-COM and French living abroad
    dep_codes = np.unique(referendum["Department code"])
    dep_codes = [el for el in dep_codes if not el.isalpha()]
    df = referendum.loc[referendum["Department code"].isin(dep_codes)].copy()

    # Merging
    for col in regions_and_departments.columns:
        df[col] = ["" for _ in range(df.shape[0])]
    for i, row in regions_and_departments.iterrows():
        dep_code = row["code_dep"]
        try:
            dep_code = str(int(dep_code))
        except:
            pass
        mask = (df["Department code"] == dep_code)
        df["code_dep"] = df["code_dep"].mask(mask, row["code_dep"]).to_numpy()
        df["name_dep"] = df["name_dep"].mask(mask, row["name_dep"]).to_numpy()
        df["code_reg"] = df["code_reg"].mask(mask, row["code_reg"]).to_numpy()
        df["name_reg"] = df["name_reg"].mask(mask, row["name_reg"]).to_numpy()

    return df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']

    Parameters
    ----------
    referendum_and_areas: pandas.DataFrame
        contains information about referendums in different departments

    Returns
    -------
    df : pandas.DataFrame
        dataframe grouped by region
    """
    df = referendum_and_areas.groupby(["name_reg"]).sum()
    df["name_reg"] = list(df.index)
    df.index = list(range(df.shape[0]))

    return df[['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']]


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.

    Parameters
    ----------
    referendum_result_by_region: pandas.DataFrame
        contains summary about the referendum by region

    Returns
    -------
    geopandas.GeoDataFrame object
    """
    region_map = gpd.read_file("./data/regions.geojson")
    # Column names: code, nom, geometry

    df = {"geometry" : list()}
    for col in referendum_result_by_regions.columns:
        df[col] = referendum_result_by_regions[col]
    for i, row in referendum_result_by_regions.iterrows():
        df["geometry"].append(region_map.loc[region_map["nom"] == row["name_reg"]]["geometry"].values[0])
    df = gpd.GeoDataFrame(df, crs=region_map.crs)
    df["ratio"] = df["Choice A"] / (df["Choice B"] + df["Choice A"])
    df.plot(column="ratio", legend=True)
    print(df[["name_reg", "ratio"]])

    return df


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    #print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
    