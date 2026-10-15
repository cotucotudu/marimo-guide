# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "marimo",
#     "plotly",
#     "polars",
#     "pyarrow",
# ]
# ///

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium", app_title="Монитор аномалий телеметрии")


@app.cell
def _():
    import marimo as mo
    import plotly.express as px
    import polars as pl

    return mo, pl, px


@app.cell
def _(mo):
    mo.md(r"""
    # Монитор аномалий телеметрии

    Данные NASA: спутник SMAP и марсоход Curiosity (MSL).
    Выберите канал и выделите участок графика мышью.
    """)
    return


@app.cell
def _(mo, pl):
    data_dir = mo.notebook_location() / "public"
    telemetry = pl.read_parquet(str(data_dir / "telemetry.parquet"))
    anomalies = pl.read_csv(str(data_dir / "anomalies.csv"))
    test = telemetry.filter(pl.col("split") == "test")
    return anomalies, test


@app.cell
def _(mo):
    spacecraft = mo.ui.dropdown(["SMAP", "MSL"], value="SMAP", label="Аппарат")
    return (spacecraft,)


@app.cell
def _(mo, pl, spacecraft, test):
    _ids = (test.filter(pl.col("spacecraft") == spacecraft.value)["chan_id"]
            .unique().sort().to_list())
    channel = mo.ui.dropdown(_ids, value=_ids[0], label="Канал")
    return (channel,)


@app.cell
def _(channel, mo, spacecraft):
    mo.hstack([spacecraft, channel], justify="start", gap=2)
    return


@app.cell
def _(anomalies, channel, pl, test):
    channel_data = test.filter(pl.col("chan_id") == channel.value)
    channel_anomalies = anomalies.filter(pl.col("chan_id") == channel.value)
    return channel_anomalies, channel_data


@app.cell
def _(channel, channel_anomalies, channel_data, mo, px):
    _fig = px.line(channel_data, x="step", y="value",
                   title=f"Канал {channel.value}")
    for _start, _end in channel_anomalies.select("start", "end").iter_rows():
        _fig.add_vrect(x0=_start, x1=_end, fillcolor="red", opacity=0.2, line_width=0)
    _fig.update_layout(dragmode="select")
    chart = mo.ui.plotly(_fig)
    return (chart,)


@app.cell
def _(channel_data, chart, mo, pl):
    if chart.value:
        _steps = [point["step"] for point in chart.value]
        selection = channel_data.filter(pl.col("step").is_in(_steps))
    else:
        selection = channel_data
    stats = mo.hstack([
        mo.stat(selection.height, label="Измерений"),
        mo.stat(int(selection["is_anomaly"].sum()), label="Аномалий"),
        mo.stat(f"{selection['value'].mean():.3f}", label="Среднее"),
    ], justify="start", gap=2)
    download = mo.download(
        data=lambda: selection.write_csv().encode("utf-8"),
        filename="selection.csv", label="Скачать выделение (CSV)",
    )
    return download, selection, stats


@app.cell
def _(channel_anomalies, chart, download, mo, selection, stats):
    mo.ui.tabs({
        "График": mo.vstack([chart, stats, download]),
        "Таблица": selection,
        "Аномалии канала": channel_anomalies,
    })
    return


if __name__ == "__main__":
    app.run()
