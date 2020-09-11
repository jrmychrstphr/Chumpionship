function apply_dynamic_styles() {

    d3.select("main").style('background', chump.colours.midnight_blue);
    
    d3.select("main").insert("div",":first-child").classed("page border top", true)
    .style("background", chump.gradients.css.blue_green);

    d3.select("main").append("div").classed("page border bottom", true)
    .style("background", chump.gradients.css.pink_blue);

    d3.selectAll(".fixture-list-wrapper, .result-list-wrapper, .league-table-wrapper").style("color", chump.colours.midnight_blue)

    d3.selectAll(".result-row.win div.indicator, .result-row.win div.score").style("background", chump.colours.green)
    d3.selectAll(".result-row.loss div.indicator, .result-row.loss div.score").style("background", chump.colours.pink)
    d3.selectAll(".result-row.draw div.indicator, .result-row.draw div.score").style("background", chump.colours.light_blue)

    d3.selectAll(".result-row.win svg rect").style("fill", chump.colours.green)
    d3.selectAll(".result-row.loss svg rect").style("fill", chump.colours.pink)
    d3.selectAll(".result-row.draw svg rect").style("fill", chump.colours.light_blue)

    d3.selectAll(".arrow-down path").style("fill", chump.colours.pink)
    d3.selectAll(".arrow-up path").style("fill", chump.colours.green)

    d3.selectAll("div.league-table-container div.table-row-container.position-first .table-column:not(.form)").style("background", chump.colours.green)
    d3.selectAll("div.league-table-container div.table-row-container.position-prize .table-column:not(.form").style("background", chump.colours.light_blue)
    d3.selectAll("div.league-table-container div.table-row-container.position-relegation .table-column:not(.form").style("background", chump.colours.pink)

}