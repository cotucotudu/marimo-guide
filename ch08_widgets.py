import marimo

__generated_with = "0.25.1"
app = marimo.App()


@app.cell
def _():
    import anywidget
    import marimo as mo
    import plotly.express as px
    import polars as pl
    import traitlets
    from wigglystuff import PlaySlider

    return PlaySlider, anywidget, mo, pl, px, traitlets


@app.cell
def _(mo, pl):
    channel_data = pl.read_parquet(
        mo.notebook_dir() / "data" / "telemetry.parquet"
    ).filter((pl.col("chan_id") == "P-1") & (pl.col("split") == "test"))
    WINDOW = 500
    return WINDOW, channel_data


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Готовый виджет: проигрыватель телеметрии
    """)
    return


@app.cell
def _(PlaySlider, WINDOW, channel_data, mo):
    player = mo.ui.anywidget(
        PlaySlider(min_value=0, max_value=channel_data.height - WINDOW,
                   step=50, interval_ms=300)
    )
    player
    return (player,)


@app.cell
def _(WINDOW, channel_data, pl, player, px):
    first = int(player.value["value"])
    window = channel_data.filter(pl.col("step").is_between(first, first + WINDOW))
    px.line(window, x="step", y="value", color="is_anomaly",
            range_y=[-1.1, 1.1], title=f"Шаги {first}–{first + WINDOW}")
    return (window,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Собственный виджет: разметка участка
    """)
    return


@app.cell
def _(anywidget, traitlets):
    class LabelWidget(anywidget.AnyWidget):
        _esm = """
        function render({ model, el }) {
          for (const name of ["норма", "аномалия"]) {
            const button = document.createElement("button");
            button.textContent = name;
            button.onclick = () => {
              model.set("label", name);
              model.save_changes();
            };
            el.appendChild(button);
          }
          const highlight = () => {
            for (const button of el.children) {
              const chosen = button.textContent === model.get("label");
              button.style.fontWeight = chosen ? "bold" : "normal";
            }
          };
          model.on("change:label", highlight);
          highlight();
        }
        export default { render };
        """
        label = traitlets.Unicode("").tag(sync=True)

    return (LabelWidget,)


@app.cell
def _(LabelWidget, mo):
    labeler = mo.ui.anywidget(LabelWidget())
    labeler
    return (labeler,)


@app.cell
def _(labeler, mo, window):
    mo.stop(not labeler.value["label"], mo.md("*Оцените участок: норма или аномалия?*"))
    truth = "аномалия" if window["is_anomaly"].any() else "норма"
    verdict = "совпадает" if labeler.value["label"] == truth else "не совпадает"
    mo.md(f"Ваша оценка: **{labeler.value['label']}**, "
          f"разметка NASA: **{truth}**. Оценка {verdict}.")
    return


if __name__ == "__main__":
    app.run()
