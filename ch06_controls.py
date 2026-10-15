import marimo

__generated_with = "0.25.1"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import polars as pl

    return mo, pl


@app.cell
def _(mo, pl):
    telemetry = pl.read_parquet(mo.notebook_dir() / "data" / "telemetry.parquet")
    test = telemetry.filter(pl.col("split") == "test")
    return (test,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Выпадающие списки и ползунок
    """)
    return


@app.cell
def _(mo):
    spacecraft = mo.ui.dropdown(["SMAP", "MSL"], value="SMAP", label="Аппарат")
    return (spacecraft,)


@app.cell
def _(mo, pl, spacecraft, test):
    channel_ids = (
        test.filter(pl.col("spacecraft") == spacecraft.value)["chan_id"]
        .unique().sort().to_list()
    )
    channel = mo.ui.dropdown(channel_ids, value=channel_ids[0], label="Канал")
    return (channel,)


@app.cell
def _(channel, mo, spacecraft):
    mo.hstack([spacecraft, channel], justify="start", gap=2)
    return


@app.cell
def _(channel, pl, test):
    channel_data = test.filter(pl.col("chan_id") == channel.value)
    return (channel_data,)


@app.cell
def _(channel_data, mo):
    steps = mo.ui.range_slider(
        start=0, stop=channel_data.height - 1, step=100,
        value=[0, channel_data.height - 1],
        show_value=True, label="Шаги",
    )
    steps
    return (steps,)


@app.cell
def _(channel_data, pl, steps):
    first, last = steps.value
    window = channel_data.filter(pl.col("step").is_between(first, last))
    return (window,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Кнопки
    """)
    return


@app.cell
def _(mo):
    counter = mo.ui.button(value=0, on_click=lambda n: n + 1, label="Нажми меня")
    run = mo.ui.run_button(label="Посчитать статистику", kind="success")
    mo.hstack([counter, run], justify="start")
    return counter, run


@app.cell
def _(counter, mo):
    mo.md(f"Число нажатий: {counter.value}")
    return


@app.cell
def _(mo, pl, run, window):
    mo.stop(not run.value, mo.md("*Нажмите «Посчитать статистику».*"))
    stats = window.select(
        pl.col("value").mean().alias("mean"),
        pl.col("value").std().alias("std"),
        pl.col("is_anomaly").sum().alias("anomalies"),
    )
    stats
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Форма
    """)
    return


@app.cell
def _(mo):
    threshold = mo.ui.number(start=1, stop=5, step=0.5, value=2,
                             label="Порог (в стандартных отклонениях)").form(
        submit_button_label="Применить"
    )
    threshold
    return (threshold,)


@app.cell
def _(mo, pl, threshold, window):
    mo.stop(threshold.value is None, mo.md("*Задайте порог и нажмите «Применить».*"))
    z = (pl.col("value") - pl.col("value").mean()) / pl.col("value").std()
    outliers = window.filter(z.abs() > threshold.value)
    mo.md(f"Точек за порогом: **{outliers.height}**")
    return (outliers,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Вкладки
    """)
    return


@app.cell
def _(mo, outliers, window):
    mo.ui.tabs({
        "Измерения": window,
        "Выбросы": outliers,
    })
    return


if __name__ == "__main__":
    app.run()
