<script>
styles = {
     core : function() {

         d3.select("main").style('background', chump.colours.midnight_blue);
         
         d3.select("main").insert("div",":first-child").classed("page border top", true)
         .style("background", chump.gradients.css.blue_green);

         d3.select("main").append("div").classed("page border bottom", true)
         .style("background", chump.gradients.css.pink_blue);

     },

     add : function() {
         
         d3.selectAll(".text.colour-white").style("color", "white")
         d3.selectAll(".text.colour-blue").style("color", chump.colours.blue)
         d3.selectAll(".text.colour-light-blue").style("color", chump.colours.light_blue)
         d3.selectAll(".text.colour-green").style("color", chump.colours.green)
         d3.selectAll(".text.colour-pink").style("color", chump.colours.pink)
         d3.selectAll(".text.colour-purple").style("color", chump.purple)
         d3.selectAll(".text.colour-light-midnight").style("color", chump.colours.light_midnight_blue)
         d3.selectAll(".text.colour-midnight").style("color", chump.colours.midnight_blue)

         d3.selectAll(".background-white").style("background", "white")
         d3.selectAll(".background-blue").style("background", chump.colours.blue)
         d3.selectAll(".background-light-blue").style("background", chump.colours.light_blue)
         d3.selectAll(".background-green").style("background", chump.colours.green)
         d3.selectAll(".background-pink").style("background", chump.colours.pink)
         d3.selectAll(".background-purple").style("background", chump.purple)
         d3.selectAll(".background-light-midnight").style("background", chump.colours.light_midnight_blue)
         d3.selectAll(".background-midnight").style("background", chump.colours.midnight_blue)

         d3.selectAll("svg .fill-white").style("fill", "white")
         d3.selectAll("svg .fill-blue").style("fill", chump.colours.blue)
         d3.selectAll("svg .fill-light-blue").style("fill", chump.colours.light_blue)
         d3.selectAll("svg .fill-green").style("fill", chump.colours.green)
         d3.selectAll("svg .fill-pink").style("fill", chump.colours.pink)
         d3.selectAll("svg .fill-purple").style("fill", chump.purple)
         d3.selectAll("svg .fill-light-midnight").style("fill", chump.colours.light_midnight_blue)
         d3.selectAll("svg .fill-midnight").style("fill", chump.colours.midnight_blue)

     }
     
 }
</script>