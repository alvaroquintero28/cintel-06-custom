import faicons as fa
import plotly.express as px
from shinywidgets import render_plotly

from shiny import reactive, render, req
from shiny.express import input, ui


# Load data and compute static values
tips = px.data.tips()
bill_rng = (min(tips.total_bill), max(tips.total_bill))


# Add page title and sidebar
ui.page_opts(title="Texas Roadhouse Tips", fillable=True)
with ui.sidebar(open="desktop", style="background-color: lightblue"):
    ui.input_slider("total_bill", "Bill Range", min=bill_rng[0], max=bill_rng[1], value=bill_rng, post="$", pre="$")
    ui.input_checkbox_group("time", "Type of Meal", ["Breakfast", "Lunch", "Happy Hour"], selected=["Breakfast", "Lunch", "Happy Hour"], inline=True)
    ui.input_action_link("reset", "Reset Filter")
    import asyncio

from shiny import reactive, render
from shiny.express import input, ui

ui.input_action_button("do_compute", "Tip Calculator")

@render.ui
@reactive.event(input.do_compute)
async def compute():
    with ui.Progress(min=1, max=10) as p:
        p.set(message="Calculation in progress", detail="This may take a while...")

        for i in range(1, 15):
            p.set(i, message="How much should I tip")
            await asyncio.sleep(0.1)

    return "Don't be cheap, Tip all you got!"
import matplotlib.pyplot as plt
import numpy as np



# Add main content
ICONS = {
    "user": fa.icon_svg("user", "solid",),
    "wallet": fa.icon_svg("dollar-sign", "solid"),
    "currency-dollar": fa.icon_svg("piggy-bank"),
    "gear": fa.icon_svg("wallet"),
   
}

with ui.layout_columns(fill=False):

    with ui.value_box(showcase=ICONS["user"], theme="bg-gradient-blue-red"):
        
        "Total tippers"
        @render.express
        def total_tippers():
            tips_data().shape[0]

    with ui.value_box(showcase=ICONS["wallet"], theme="bg-gradient-blue-red"):
        
        "Average tip"
        @render.express
        def average_tip():
            d = tips_data()
            if d.shape[0] > 0:
                perc = d.tip / d.total_bill
                f"{perc.mean():.1%}"
    
    with ui.value_box(showcase=ICONS["currency-dollar"], theme="bg-gradient-blue-red"):
        "Average Tab"
        @render.express
        def average_bill():
            d = tips_data()
            if d.shape[0] > 0:
                bill = d.total_bill.mean()
                f"${bill:.2f}"


with ui.layout_columns(col_widths=[6, 6, 12]):

    with ui.card(full_screen=True, style="background-color: teal"):
        ui.card_header("Tips Grid")
        @render.data_frame
        def table():
            return render.DataGrid(tips_data())

    with ui.card(full_screen=True, style="background-color: teal"):
        with ui.card_header(class_="d-flex justify-content-between align-items-center"):
            "Total Tab vs Tip Amount"
            with ui.popover(title="Add a color variable", placement="top"):
                ICONS["gear"]
                ui.input_radio_buttons(
                    "scatter_color", None,
                    ["none", "sex", "day", "time"],
                    inline=True
                )

        @render_plotly
        def scatterplot():
            color = input.scatter_color()
            return px.scatter(
                tips_data(),
                x="total_bill",
                y="tip",
                color=None if color == "none" else color,
                trendline="lowess"
            )

    with ui.card(full_screen=True, style="background-color: teal"):
        with ui.card_header(class_="d-flex justify-content-between align-items-center"):
            "Tip percentages"
            with ui.popover(title="Add a color variable"):
                ICONS["gear"]
                ui.input_radio_buttons(
                    "tip_perc_y", "Split by:",
                    ["sex", "day", "time"],
                    selected="day",
                    inline=True
                )

        @render_plotly
        def tip_perc():
            from ridgeplot import ridgeplot
            # Must make a copy of this Pandas dataframe before we mutate it!
            # See https://shiny.posit.co/py/docs/reactive-mutable.html
            dat = tips_data().copy()
            dat["percent"] = dat.tip / dat.total_bill
            yvar = input.tip_perc_y()
            uvals = dat[yvar].unique()

            samples = [
                [ dat.percent[dat[yvar] == val] ]
                for val in uvals
            ]

            plt = ridgeplot(
                samples=samples, labels=uvals, bandwidth=0.01,
                colorscale="viridis", colormode="row-index"
            )

            plt.update_layout(
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
            )

            return plt


# --------------------------------------------------------
# Reactive calculations and effects
# --------------------------------------------------------

@reactive.calc
def tips_data():
    bill = input.total_bill()
    idx1 = tips.total_bill.between(bill[0], bill[1])
    idx2 = tips.time.isin(input.time())
    return tips[idx1 & idx2]

@reactive.effect
@reactive.event(input.reset)
def _():
    ui.update_slider("total_bill", value=bill_rng)
    ui.update_checkbox_group("time", selected=["Breakfast", "Lunch", "Happy Hour"])
