# Import necessary modules first
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely import MultiPolygon
from shapely.geometry import Point, LineString, Polygon
import fiona
import folium
import matplotlib.pyplot as plt

plt.style.use("bmh")

connections_df = pd.read_csv("csv/connections.csv", index_col="id")
sources_df = pd.read_csv("csv/sources.csv", index_col="id")
topics_df = pd.read_csv("csv/topics.csv", index_col="id")

# TODO: Figure out the GeoPandas/Pandas way to "MERGE"
# merged_sources_df = sources_df.merge(topics_df, left_on="topic_id", right_index=True)
# print(merged_sources_df.head())

sources_df["x"] = sources_df["vector_2d"].apply(
    lambda vector_2d: float(vector_2d.strip("[]").split(",")[0])
)
sources_df["y"] = sources_df["vector_2d"].apply(
    lambda vector_2d: float(vector_2d.strip("[]").split(",")[1])
)
sources_df["topic"] = sources_df["topic_id"].apply(
    lambda topic_id: topics_df.loc[topic_id, "name"]
)

# Normalize x and y to -180 to 180 and -90 to 90
min_x, min_y = sources_df[["x", "y"]].min()
max_x, max_y = sources_df[["x", "y"]].max()
min_val = min(min_x, min_y)
max_val = max(max_x, max_y)
val_range = max_val - min_val
sources_df["x"] = ((sources_df["x"] - min_val) / (val_range) * 360 / 2) - 180 / 2
sources_df["y"] = ((sources_df["y"] - min_val) / (val_range) * 180 / 2) - 90 / 2

# print(sources_df["x"].min(), sources_df["x"].max())
# print(sources_df["y"].min(), sources_df["y"].max())


df = {
    "Topic": sources_df["topic"],
    "Url": sources_df["url"],
    "geometry": gpd.points_from_xy(sources_df["x"], sources_df["y"]),
    # "geometry": [Point(-87.789, 41.976)],
}
gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")
gdf = gdf.to_crs(epsg=3857)


def compute_convex_hulls(geometry):
    if geometry.geom_type == "MultiPolygon":
        return MultiPolygon([poly.convex_hull for poly in geometry.geoms])
    elif geometry.geom_type == "Polygon":
        return geometry.convex_hull
    else:
        return geometry  # Keep other geometry types unchanged


buf = gdf.copy()
buf["geometry"] = buf["geometry"].apply(lambda x: x.buffer(100000))
# buf = gdf.buffer(distance=100000)
# buf = gpd.GeoDataFrame(
#     {"Topic": gdf["Topic"], "geometry": buf}, geometry="geometry", crs="EPSG:3857"
# )

dissolved_gdf = buf.dissolve(by="Topic")
convex_gdf = dissolved_gdf.copy()
convex_gdf["geometry"] = convex_gdf["geometry"].apply(compute_convex_hulls)

# bp = buf.plot()
# gdf.plot(ax=bp, color="red")
# plt.show()

gdf.to_crs(epsg=4326).to_file(
    "leaflet-app/public/geojson/points.geojson", driver="GeoJSON"
)
convex_gdf.to_crs(epsg=4326).to_file(
    "leaflet-app/public/geojson/convex.geojson", driver="GeoJSON"
)

m = convex_gdf.explore(
    # tiles="OpenStreetMap",
    tiles=None,
    # marker_kwds={
    #     "radius": 3,
    #     # "color": "red",
    #     "tooltip": gdf["Topic"],
    # },
    # location=[
    #     gdf.geometry.centroid.y.mean(),
    #     gdf.geometry.centroid.x.mean(),
    # ],  # Center on point
    # zoom_start=15,  # Zoom in close
)


# m = folium.Map(
#     location=[gdf.geometry.y.mean(), gdf.geometry.x.mean()], zoom_start=10, tiles=None
# )

# for _, row in gdf.iterrows():
#     folium.CircleMarker(
#         location=[row.geometry.y, row.geometry.x],
#         radius=3,
#         color="red",
#         fill=True,
#         fill_color="red",
#         fill_opacity=0.6,
#     ).add_to(m)

#     folium.Marker(
#         location=[row.geometry.y, row.geometry.x],
#         # popup=None,
#         # icon=folium.Icon(color="red", icon="info-sign"),
#         icon=folium.DivIcon(
#             html=f'<div style="font-size: 12pt; color: red; font-weight: bold;">{row["Topic"]}</div>',
#         ),
#         # Optional: Define the zoom levels at which the text label will be visible
#         icon_size=(150, 36),
#         max_zoom=18,  # Text will be visible only when zoomed in enough
#         min_zoom=10,  # Text will appear starting from zoom level 10
#         # tooltip=row["Topic"],  # This is the text that will appear on hover
#     ).add_to(m)


m.save("map.html")
