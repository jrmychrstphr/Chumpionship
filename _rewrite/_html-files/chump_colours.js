chump_colours = {}

chump_colours.green = d3.rgb("#00FF00");
chump_colours.blue = d3.rgb("#0000FF");
chump_colours.teal = d3.rgb( function() {

		s = d3.scaleLinear()
        .domain([0, 2])
        .range([chump_colours.green, chump_colours.blue])
        .interpolate(d3.interpolateRgb);

        return s(1)
		
	} () );
chump_colours.grey = d3.rgb("#4a4a4a");