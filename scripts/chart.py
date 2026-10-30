"""Interactive chart of women's participation in Chilean elections."""

import altair as alt

from mujeres_en_elecciones.data_loading import load_candidate_data

# 1. APPEARANCE ---------------------------------------------------------------
FEMALE_COLOR = "#9569ca"
MALE_COLOR = "#28716e"
LINE_COLOR = "#d76b91"
LINE_OUTLINE = "#fffefa"
BACKGROUND_COLOR = "#d8f3f2"
TEXT_COLOR = "#352b64"

CHART_HEIGHT = 450
# Reference width of the plotting area (excluding legend and axes).
# Adjust if the chart container changes substantially.
PLOT_WIDTH_REFERENCE = 900
BAR_MAX_WIDTH = 65
BAR_MIN_WIDTH = 30
BAR_FILL_RATIO = 0.6
LABEL_FILL_RATIO = 0.8

EXCLUDED_ELECTIONS = {
    "PRIMARIAS PRESIDENCIALES",
    "CONSEJO CONSTITUCIONAL GENERAL",
    "CONSEJO CONSTITUCIONAL PUEBLOS INDIGENAS",
    "CONVENCIONALES CONSTITUYENTES GENERALES",
    "CONVENCIONALES CONSTITUYENTES PUEBLOS INDIGENAS",
    "GOBERNADORES REGIONALES",
    "GOBERNADORES REGIONALES 2a V",
    "PRESIDENCIAL",
    "PRESIDENCIAL 2a V",
    "PRIMARIAS DIPUTADOS",
    "PRIMARIAS ALCALDES",
    "PRIMARIAS GOBERNADORES REGIONALES",
}

EXCLUDED_RESULTS = {
    "NO ELECTO",
    "PRESIDENTE",
    "SELECCIONADO SEGUNDA VOTACION",
    "NO NOMINADO",
    "NOMINADO",
    "CCG",
    "CCPI",
}

# 2. DATA ---------------------------------------------------------------------
data = load_candidate_data().rename(
    columns={
        "año": "year",
        "elección": "election",
        "sexo": "sex",
        "resultado en elección": "election_result",
    }
)

options = sorted(set(data["election"].dropna().unique()) - EXCLUDED_ELECTIONS)
initial_election = "ALCALDES" if "ALCALDES" in options else options[0]
data = data[data["election"].isin(options)].copy()

candidate_counts = (
    data.groupby(["election", "year", "sex"]).size().reset_index(name="candidate_count")
)
candidate_counts["candidate_percentage"] = (
    candidate_counts["candidate_count"]
    / candidate_counts.groupby(["election", "year"])["candidate_count"].transform("sum")
    * 100
)
candidate_counts["label"] = candidate_counts["sex"].map(
    {"MUJER": "Female Candidates", "HOMBRE": "Male Candidates"}
)

# Adapt bar and annotation widths to the number of years in each election.
# Vega-Lite reads these per-record sizes after the dropdown filter is applied.
years_per_election = candidate_counts.groupby("election")["year"].nunique()
width_by_election = (PLOT_WIDTH_REFERENCE / years_per_election * BAR_FILL_RATIO).clip(
    lower=BAR_MIN_WIDTH, upper=BAR_MAX_WIDTH
)
candidate_counts["bar_width"] = candidate_counts["election"].map(width_by_election)
candidate_counts["label_width"] = candidate_counts["bar_width"] * LABEL_FILL_RATIO

# Preserve the original elected-result classification; validate separately.
successful_candidates = data[~data["election_result"].isin(EXCLUDED_RESULTS)].copy()
successful_counts = (
    successful_candidates.groupby(["election", "year", "sex"])
    .size()
    .reset_index(name="successful_count")
)
successful_counts["successful_percentage"] = (
    successful_counts["successful_count"]
    / successful_counts.groupby(["election", "year"])["successful_count"].transform(
        "sum"
    )
    * 100
)
successful_women = successful_counts[successful_counts["sex"] == "MUJER"].copy()
successful_women["series"] = "Elected Women"
successful_women["label_width"] = (
    successful_women["election"].map(width_by_election) * LABEL_FILL_RATIO
)

# Position the pink annotation just above each elected-women point.
line_label_data = successful_women.copy()
line_label_data["label_y"] = (line_label_data["successful_percentage"] + 5.5).clip(
    upper=96
)
line_label_data["box_bottom"] = line_label_data["label_y"] - 2.2
line_label_data["box_top"] = line_label_data["label_y"] + 2.2
line_label_data["percentage_label"] = line_label_data["successful_percentage"].map(
    lambda value: f"{value:.1f}%"
)

# Annotation locations: women near the bottom of the purple segment, men near
# the top of the teal segment. Keeps the pink line and labels distinct.
bar_label_data = candidate_counts.copy()
bar_label_data["label_y"] = bar_label_data.apply(
    lambda row: (
        min(6.0, row["candidate_percentage"] / 2)
        if row["sex"] == "MUJER"
        else 100 - min(5.0, row["candidate_percentage"] / 2)
    ),
    axis=1,
)
bar_label_data["box_bottom"] = (bar_label_data["label_y"] - 2.2).clip(lower=0)
bar_label_data["box_top"] = (bar_label_data["label_y"] + 2.2).clip(upper=100)
bar_label_data["percentage_label"] = bar_label_data["candidate_percentage"].map(
    lambda value: f"{value:.1f}%"
)

tooltip_data = candidate_counts.pivot_table(
    index=["election", "year"],
    columns="sex",
    values=["candidate_count", "candidate_percentage"],
    aggfunc="first",
)
tooltip_data.columns = [
    f"{metric}_{sex.lower()}" for metric, sex in tooltip_data.columns
]
tooltip_data = tooltip_data.reset_index().merge(
    successful_women[["election", "year", "successful_count", "successful_percentage"]],
    on=["election", "year"],
    how="left",
)
tooltip_data["hover_width"] = tooltip_data["election"].map(width_by_election) * 1.08

# 3. SELECTION AND SHARED ENCODINGS -------------------------------------------
election_selection = alt.selection_point(
    fields=["election"],
    bind=alt.binding_select(options=options, name="Election type: "),
    value=[{"election": initial_election}],
)

x_axis = alt.X(
    "year:O",
    title="Year",
    sort="ascending",
    axis=alt.Axis(
        labelAngle=0,
        labelFont="Nunito",
        labelFontSize=12,
        titleFont="Nunito",
        titleFontSize=14,
        labelColor=TEXT_COLOR,
        titleColor=TEXT_COLOR,
        grid=False,
    ),
)
y_scale = alt.Scale(domain=[0, 100], nice=False)
y_axis = alt.Y(
    "candidate_percentage:Q",
    title="Percentage",
    scale=y_scale,
    axis=alt.Axis(
        labelExpr="datum.value + '%'",
        values=[0, 20, 40, 60, 80, 100],
        labelFont="Nunito",
        labelFontSize=12,
        titleFont="Nunito",
        titleFontSize=14,
        labelColor=TEXT_COLOR,
        titleColor=TEXT_COLOR,
        grid=True,
        gridColor="#e8e5e9",
    ),
)
series_scale = alt.Scale(
    domain=["Female Candidates", "Male Candidates", "Elected Women"],
    range=[FEMALE_COLOR, MALE_COLOR, LINE_COLOR],
)
series_legend = alt.Legend(
    title=None,
    orient="right",
    direction="vertical",
    labelFont="Nunito",
    labelFontSize=13,
    labelColor=TEXT_COLOR,
    symbolSize=160,
)

# 4. STACKED BARS -------------------------------------------------------------
bars = (
    alt.Chart(candidate_counts)
    .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
    .encode(
        x=x_axis,
        y=y_axis,
        size=alt.Size("bar_width:Q", scale=None, legend=None),
        color=alt.Color("label:N", scale=series_scale, legend=series_legend),
        order=alt.Order("label:N", sort="ascending"),
    )
    .transform_filter(election_selection)
)

# Light rectangular annotation backgrounds, with labels centered on top.
label_boxes = (
    alt.Chart(bar_label_data)
    .mark_bar(color=LINE_OUTLINE, opacity=0.92, cornerRadius=4)
    .encode(
        x=alt.X("year:O", sort="ascending"),
        y=alt.Y("box_top:Q", scale=y_scale),
        y2="box_bottom:Q",
        size=alt.Size("label_width:Q", scale=None, legend=None),
    )
    .transform_filter(election_selection)
)
bar_labels = (
    alt.Chart(bar_label_data)
    .mark_text(
        font="Nunito",
        fontSize=13,
        fontWeight="bold",
        color=TEXT_COLOR,
        align="center",
        baseline="middle",
    )
    .encode(
        x=alt.X("year:O", sort="ascending"),
        y=alt.Y("label_y:Q", scale=y_scale),
        text="percentage_label:N",
    )
    .transform_filter(election_selection)
)

# 5. ELECTED-WOMEN LINE -------------------------------------------------------
line_base = (
    alt.Chart(successful_women)
    .encode(
        x=alt.X("year:O", sort="ascending"),
        y=alt.Y("successful_percentage:Q", scale=y_scale),
        color=alt.Color("series:N", scale=series_scale, legend=series_legend),
    )
    .transform_filter(election_selection)
)
line_border = line_base.mark_line(
    color=LINE_OUTLINE, strokeWidth=8, interpolate="monotone"
)
line = line_base.mark_line(color=LINE_COLOR, strokeWidth=4, interpolate="monotone")
points = line_base.mark_point(
    filled=True,
    size=110,
    color=LINE_COLOR,
    stroke=LINE_OUTLINE,
    strokeWidth=2,
)
# Pink annotation boxes and white percentages above the curve.
line_label_boxes = (
    alt.Chart(line_label_data)
    .mark_bar(color=LINE_COLOR, cornerRadius=4)
    .encode(
        x=alt.X("year:O", sort="ascending"),
        y=alt.Y("box_top:Q", scale=y_scale),
        y2="box_bottom:Q",
        size=alt.Size("label_width:Q", scale=None, legend=None),
    )
    .transform_filter(election_selection)
)
line_labels = (
    alt.Chart(line_label_data)
    .mark_text(
        font="Nunito",
        fontSize=13,
        fontWeight="bold",
        color="#ffffff",
        align="center",
        baseline="middle",
    )
    .encode(
        x=alt.X("year:O", sort="ascending"),
        y=alt.Y("label_y:Q", scale=y_scale),
        text="percentage_label:N",
    )
    .transform_filter(election_selection)
)

# 6. COMBINED TOOLTIP ---------------------------------------------------------
tooltip_layer = (
    alt.Chart(tooltip_data)
    .mark_bar(opacity=0)
    .encode(
        x=alt.X("year:O", sort="ascending"),
        y=alt.value(0),
        y2=alt.value(CHART_HEIGHT),
        size=alt.Size("hover_width:Q", scale=None, legend=None),
        tooltip=[
            alt.Tooltip("year:O", title="Year"),
            alt.Tooltip("successful_count:Q", title="Elected women", format=","),
            alt.Tooltip(
                "successful_percentage:Q", title="Elected women (%)", format=".1f"
            ),
            alt.Tooltip(
                "candidate_count_hombre:Q", title="Male candidates", format=","
            ),
            alt.Tooltip(
                "candidate_percentage_hombre:Q",
                title="Male candidates (%)",
                format=".1f",
            ),
            alt.Tooltip(
                "candidate_count_mujer:Q", title="Female candidates", format=","
            ),
            alt.Tooltip(
                "candidate_percentage_mujer:Q",
                title="Female candidates (%)",
                format=".1f",
            ),
        ],
    )
    .transform_filter(election_selection)
)

# 7. FINAL CHART --------------------------------------------------------------
chart = (
    alt.layer(
        bars,
        label_boxes,
        bar_labels,
        line_border,
        line,
        points,
        line_label_boxes,
        line_labels,
        tooltip_layer,
    )
    .add_params(election_selection)
    .properties(
        width="container",
        height=CHART_HEIGHT,
        background=BACKGROUND_COLOR,
        padding={"left": 25, "right": 25, "top": 25, "bottom": 25},
    )
    .configure_view(fill=BACKGROUND_COLOR, stroke=None, cornerRadius=16)
    .configure(font="Nunito")
)
