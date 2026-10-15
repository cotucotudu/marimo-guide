import marimo

__generated_with = "0.25.1"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import plotly.express as px
    import polars as pl

    return mo, pl, px


@app.cell
def _(mo, pl):
    telemetry = pl.read_parquet(mo.notebook_dir() / "data" / "telemetry.parquet")
    anomalies = pl.read_csv(mo.notebook_dir() / "data" / "anomalies.csv")
    test = telemetry.filter(pl.col("split") == "test")
    return anomalies, test


@app.cell
def _(mo, test):
    channel = mo.ui.dropdown(
        sorted(test["chan_id"].unique().to_list()), value="P-1", label="Канал"
    )
    channel
    return (channel,)


@app.cell
def _(anomalies, channel, pl, test):
    channel_data = test.filter(pl.col("chan_id") == channel.value)
    channel_anomalies = anomalies.filter(pl.col("chan_id") == channel.value)
    return channel_anomalies, channel_data


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. График plotly с отмеченными аномалиями
    """)
    return


@app.cell
def _(channel, channel_anomalies, channel_data, px):
    fig = px.line(channel_data, x="step", y="value",
                  title=f"Телеметрия канала {channel.value}")
    for _start, _end in channel_anomalies.select("start", "end").iter_rows():
        fig.add_vrect(x0=_start, x1=_end, fillcolor="red", opacity=0.2, line_width=0)
    fig.update_layout(dragmode="select")
    return (fig,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Выделение на графике
    """)
    return


@app.cell
def _(fig, mo):
    chart = mo.ui.plotly(fig)
    chart
    return (chart,)


@app.cell
def _(channel_data, chart, mo, pl):
    mo.stop(not chart.value, mo.md("*Выделите участок графика мышью.*"))
    selected_steps = [point["step"] for point in chart.value]
    selection = channel_data.filter(pl.col("step").is_in(selected_steps))
    share = selection["is_anomaly"].mean()
    mo.vstack([
        mo.md(f"Выделено точек: **{selection.height}**; "
              f"доля аномалий: **{share:.0%}**"),
        selection,
    ])
    return


if __name__ == "__main__":
    app.run()
