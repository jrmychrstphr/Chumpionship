  <script>
  /* updated: Aug 24 (results) */
   styles = {
        core : function() {

            d3.select("main").style('background', chump.colours.midnight_blue);
            
            d3.select("main").insert("div",":first-child").classed("page border top", true)
            .style("background", chump.gradients.css.blue_green);

            d3.select("main").append("div").classed("page border bottom", true)
            .style("background", chump.gradients.css.pink_blue);

        },

        add : function() {
            
            d3.selectAll(".text.colour-midnight").style("color", chump.colours.midnight_blue)
            d3.selectAll(".text.colour-white").style("color", "white")
            //d3.selectAll(".fixture-list-wrapper, .result-list-wrapper, .league-table-wrapper, .legend-item").style("color", chump.colours.midnight_blue)

            d3.selectAll(".background-white").style("background", "white")
            d3.selectAll(".background-light-midnight").style("background", chump.colours.light_midnight_blue)

            d3.selectAll(".result-row .result-color.win").style("background", chump.colours.green)
            d3.selectAll(".result-row .result-color.loss").style("background", chump.colours.pink)
            d3.selectAll(".result-row .result-color.draw").style("background", chump.colours.light_blue)

            d3.selectAll(".result-row.win svg rect").style("fill", chump.colours.green)
            d3.selectAll(".result-row.loss svg rect").style("fill", chump.colours.pink)
            d3.selectAll(".result-row.draw svg rect").style("fill", chump.colours.light_blue)

            d3.selectAll(".arrow-down path").style("fill", chump.colours.pink)
            d3.selectAll(".arrow-up path").style("fill", chump.colours.green)

            d3.selectAll("div.league-table-container div.table-row-container.position-first .table-column:not(.viz)").style("background", chump.colours.green)
            d3.selectAll("div.league-table-container div.table-row-container.position-prize .table-column:not(.viz").style("background", chump.colours.light_blue)
            d3.selectAll("div.league-table-container div.table-row-container.position-relegation .table-column:not(.viz").style("background", chump.colours.pink)

            //bubble-pack viz
            d3.selectAll("div.viz svg .colour-gkp").style("fill", chump.colours.purple)
            d3.selectAll("div.viz svg .colour-def").style("fill", chump.colours.green)
            d3.selectAll("div.viz svg .colour-mid").style("fill", chump.colours.light_blue)
            d3.selectAll("div.viz svg .colour-fwd").style("fill", chump.colours.pink)
            d3.selectAll("div.viz svg .colour-white").style("fill", "white")

            d3.selectAll("div.viz.bubble-pack svg text:not(.colour-gkp):not(.colour-def):not(.colour-mid):not(.colour-fwd):not(.colour-white)").style("fill", chump.colours.midnight_blue)

        }
        
    }
  </script>