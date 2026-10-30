# Women in Chilean Elections

An analysis of women's representation in Chilean elections, using candidate records from the Chilean Electoral Service (SERVEL).

**[Explore the interactive chart](https://loretoaguero.github.io/candidatas_chile/)**

The chart compares the share of female and male candidates with the share of women among elected candidates, by election type and year. Use the dropdown to select an election and hover over the chart to explore the figures.

## Data

The main dataset is `data/raw/historial_del_candidato_1989-2025_v1.csv`, covering candidate records for 1989–2025. The repository also contains municipal election Excel files.

The report identifies SERVEL as the source and links to its [data dashboard](https://app.powerbi.com/view?r=eyJrIjoiMTExOTgwZjItZDU4OS00NTdiLThmODgtMGVhY2E2MDk3MzI4IiwidCI6IjI0ODMxZWJlLWQyNmQtNGQzMC05ZmE4LWVmM2MwMjQzYjMyZSIsImMiOjR9).

Original source files are kept in `data/raw/`. Preserve these files unchanged and store any future processed datasets separately.

## Project structure

- `src/mujeres_en_elecciones/data_loading.py`: reusable CSV and Excel loading functions.
- `scripts/chart.py`: data aggregation and interactive Altair chart definition.
- `scripts/main.py`: example of loading municipal election data.
- `reports/women_candidates.qmd`: Quarto report with context, findings, and the chart; the narrative is currently in French.
- `reports/styles.css`: report styling.
- `index.html`: exported chart served as the GitHub Pages homepage.
- `pyproject.toml` and `uv.lock`: Python dependencies and locked environment.

## Set up the environment

Install [uv](https://docs.astral.sh/uv/), then run from the repository root:

```bash
uv sync
```

The project requires Python 3.14 or later, as specified in `pyproject.toml`.

To run the municipal data-loading example:

```bash
uv run python scripts/main.py
```

## Generate the interactive chart

Run this command from the repository root to regenerate the published chart using the current chart code and source data:

```bash
uv run python -c 'import runpy; runpy.run_path("scripts/chart.py")["chart"].save("index.html")'
```

Open `index.html` in a browser to inspect the result. The standard Altair HTML export loads JavaScript libraries from a CDN and requires an internet connection.

The checked-in HTML is a snapshot: editing the Python code or datasets does not automatically update it. Regenerate and review the HTML before publishing changes.

## Render the report

Rendering the full report also requires the [Quarto CLI](https://quarto.org/). Register the Jupyter kernel referenced by the report:

```bash
uv run python -m ipykernel install --user --name mujeres_en_elecciones --display-name "Mujeres en Elecciones"
uv run quarto render reports/women_candidates.qmd
```

The report output is separate from the root `index.html` chart.

## Methodology and scope

Data validation was carried out in separate Jupyter notebooks that will be added to this repository. The chart script focuses on aggregation and visualization; it does not reproduce all validation steps.

- Candidate percentages are calculated within each election type and year, using records with non-missing grouping fields. Counts represent dataset rows; the chart script itself does not perform deduplication.
- The source field `sexo` supplies the observed categories `MUJER` and `HOMBRE`, displayed as “Female Candidates” and “Male Candidates.” These source categories should not be interpreted as inferred gender identity. Missing demographic information is not inferred or filled in.
- The elected-women percentage uses all records classified as elected as its denominator. It is not the percentage of female candidates who won.
- Elected status is derived by excluding a list of election-result labels in `scripts/chart.py`. The supporting validation is in the separate notebooks, which are not yet included in this repository.
- The chart excludes presidential elections, regional governor elections, constitutional bodies, and the primary election categories listed in `EXCLUDED_ELECTIONS` in `scripts/chart.py`.
- Available years vary by election type. Figures describe the records in the source dataset and the elections held in each year, rather than the full composition of an institution between elections.

## Publishing

GitHub Pages is configured to serve the repository root on the `main` branch. After regenerating `index.html`, commit and push the reviewed changes to update the published chart. Deployment progress is available in the repository's **Actions** tab.

## Code quality

Use Ruff for Python linting and formatting:

```bash
uv run ruff check .
uv run ruff format --check .
```

Use pytest when adding tests for data transformations. It is not currently listed among the project's dependencies.
