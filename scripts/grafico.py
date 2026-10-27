import plotly.express as px

from mujeres_en_elecciones.data_loading import load_candidate_data

data = load_candidate_data()

datos_muni = data[data["elección"] == "ALCALDES"]

conteo_muni = datos_muni.groupby(["año", "sexo"]).size().reset_index(name="counts")

conteo_muni_elegidos = (
    datos_muni[datos_muni["resultado en elección"] == "ALCALDE"]
    .groupby(["año", "sexo"])
    .size()
    .reset_index(name="counts")
)

conteo_muni_con_elegidos = conteo_muni.merge(
    conteo_muni_elegidos, on=["año", "sexo"], how="left", suffixes=("", "_elegidos")
)

conteo_muni_con_elegidos["porcentaje"] = (
    conteo_muni_con_elegidos["counts_elegidos"]
    / conteo_muni_con_elegidos.groupby(["año", "sexo"])["counts"].transform("sum")
    * 100
)

fig = px.line(
    conteo_muni_con_elegidos,
    x="año",
    y="porcentaje",
    color="sexo",
    markers=True,
    color_discrete_map={
        "F": "#9569ca",
        "M": "#28716e",
    },
    labels={"año": "Año", "porcentaje": "Porcentaje", "sexo": "Sexo"},
    title="Porcentaje de candidaturas a alcaldes por sexo",
)


fig.update_layout(
    # template="plotly_white",
    # font_family="Inter",
    plot_bgcolor="#fffefa",
    paper_bgcolor="#d8f3f2",
    margin={"t": 80, "l": 80},
)

fig.update_yaxes(ticksuffix="%", rangemode="tozero")
fig.show()
