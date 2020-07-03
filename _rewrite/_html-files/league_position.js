function league_position(manager_code) {

    if (!(manager_code)) {
        manager_code = '55259'
    }

	// Compile a dataset from the database
    // Total transfers made by gameweek
    dataset = []            

    //for each player in the database
    $.each( database['player_data'], function(key, val) {

        var gameweeks_played = return_gameweeks_played(database)


	        // for each gameweek
	        for ( idx = 0; idx < gameweeks_played; idx++ ) {
	            var gameweek = idx+1
	            var position = val['season_performance']['league_position_array'][idx]

	            temp_obj = {
	                'manager_code': key,
	                'gameweek': gameweek,
	                'league_position': position
	            }

	            dataset.push(temp_obj)
	        }


    })

    console.log(dataset)

    // add big numbers
    d3.select('#highest-league-position div.dynamic-content')
    .text(return_ordinal_suffix_of(d3.min(dataset.filter(function(d) { return d.manager_code === manager_code }), d => d.league_position) ) )

    d3.select('#lowest-league-position div.dynamic-content')
    .text(return_ordinal_suffix_of(d3.max(dataset.filter(function(d) { return d.manager_code === manager_code }), d => d.league_position) ) )
    
    d3.select('#average-league-position div.dynamic-content')
    .text(d3.format(".1f")(d3.mean(dataset.filter(function(d) { return d.manager_code === manager_code }), d => d.league_position)) )

    

    //Build dataviz -- position over time
    viz_div = $("#league-position-over-time .dynamic-content")

    dataviz_config = {
        'viz_height': viz_div.height(),
        'viz_width': viz_div.width(),
        'canvas_padding': {
            'top': 1,
            'right': 20,
            'bottom': 35,
            'left': 50
        }
    }


    var viz_container = d3.select("#league-position-over-time .dynamic-content")

    var svg = viz_container.append("svg")
    .attr('height', dataviz_config.viz_height)
    .attr('width', dataviz_config.viz_width);

    // define scales

    // xScale
    var xDomain = d3.extent(dataset, d => d.gameweek)
    console.log(xDomain)        

    var xScale = d3.scaleLinear()
    .domain(xDomain)
    .range([dataviz_config.canvas_padding.left, (dataviz_config.viz_width - dataviz_config.canvas_padding.right)]);

    //yScale
    var yDomain = function() {
        temp_array = []
        e = d3.extent( dataset, d => d.league_position )

        console.log(e)

        for ( i = e[0]; i <= e[1]; i++ ) {
            temp_array.push(i)
        }

        return temp_array
    } ()

    var yScale = d3.scaleBand()
    .domain(yDomain)   
    .range([dataviz_config.canvas_padding.top, (dataviz_config.viz_height - dataviz_config.canvas_padding.bottom)]);


    // Add table shading and lines
    regions_data = [
        {'start': 1, 'end': 4, 'fill': chump_colours.dark_grey },
        {'start': 18, 'end': 20, 'fill': chump_colours.dark_grey }
    ]

    lines_data = [
        //{'position': 1, 'type': 'dashed'},
        {'position': 4, 'type': 'solid'},
        {'position': 17, 'type': 'solid'}
    ]

    var axisRegions = svg.append('g')
    .classed('axisRegions', true);

    axisRegions.selectAll('.axisRegion')
    .data(regions_data)
    .enter()
    .append('rect')
    .classed('.axisRegion', true)
    .attr('width', dataviz_config.viz_width )
    .attr('height', function(d) {
        p = d.end - d.start
        h = yScale.bandwidth() * (p+1)

        return h
    })
    .style('transform', function(d) {
        t = 'translateY(' + yScale( d.start ) + 'px)'
        return t
        })
    .style('fill', d => d.fill )
    .style('stroke', 'black')

    var axisLines = svg.append('g')
    .classed('axisLines', true);

    // add dotted line at the fold
    var the_fold = axisLines.append('line')
    .attr('x1', 0)
    .attr('x2', dataviz_config.viz_width)
    .attr('y1', function(d) { return yScale( d3.max(yDomain)/2 ) + yScale.step() })
    .attr('y2', function(d) { return yScale( d3.max(yDomain)/2  ) + yScale.step() })
    .style('stroke', chump_colours.grey)
    .style('stroke-width', '1px')
    .style('stroke-dasharray',"5,5")

    // add line at the top
    axisLines.append('line')
    .attr('x1', 0)
    .attr('x2', dataviz_config.viz_width)
    .attr('y1', dataviz_config.canvas_padding.top )
    .attr('y2', dataviz_config.canvas_padding.top )
    .style('stroke', chump_colours.dark_grey)
    .style('stroke-width', '1px')

    // add line at the bottom
    axisLines.append('line')
    .attr('x1', 0)
    .attr('x2', dataviz_config.viz_width)
    .attr('y1', dataviz_config.viz_height - dataviz_config.canvas_padding.bottom )
    .attr('y2', dataviz_config.viz_height - dataviz_config.canvas_padding.bottom )
    .style('stroke', chump_colours.dark_grey)
    .style('stroke-width', '1px')

    //add axes

    //xAxis
    var xAxisGenerator = d3.axisBottom(xScale)
    .tickSizeOuter(0)
    .tickSize(10)
    .tickPadding(10)
    .tickValues(function() {
        // 1, max and every 10
        var temp_array = [];
        var domain = xDomain

        //console.log('domain.length ' + domain.length)

        for (i = domain[0]; i <= domain[1]; i++ ){

            if (i === domain[0] || i === domain[1] && (domain[1] % 10) > 2 || i % 10 === 0) { 
                temp_array.push(i)
             }
        }

        return temp_array

    } ())
    .tickFormat(d => ("GW"+ d));

    var xAxis = svg.append("g")
    .classed("x axis", true)
    .call(xAxisGenerator);

    xAxis.select(".domain").remove();
    xAxis.attr('transform', function(d) {
            return 'translate(0 ' + (dataviz_config.viz_height - dataviz_config.canvas_padding.bottom) + ')';
        });
    
    var xAxisGrid = xAxisGenerator
    .tickSize(dataviz_config.viz_height - dataviz_config.canvas_padding.bottom)
    .tickSizeOuter(0)
    .tickFormat("");

    svg.append("g")
    .attr("class", "x axis-grid")
    .call(xAxisGrid)
    .select(".domain").remove();


    //yAxis
    var yAxisGenerator = d3.axisLeft(yScale)
    .tickSizeOuter(0)
    .tickSize(0)

    var yAxis = svg.append("g")
    .classed("y axis", true)
    .call(yAxisGenerator);

    yAxis.select(".domain").remove();
    yAxis.selectAll(".tick text").attr('dy', '0.3em');
    yAxis.style('transform', 'translateX(25px)');


    //colors
    var defs = svg.append("defs")

    var colours_scale = d3.scaleLinear()
    .domain(d3.extent(yDomain))
    .range([chump_colours.green, chump_colours.blue])
    .interpolate(d3.interpolateRgb);


    // data
    var data_layer = svg.append('g')
    .classed('data-layer', true)


    var data_path = data_layer.append('path')
    .datum(dataset.filter(function(d) { return d.manager_code === manager_code }))
    .attr("d", d3.line()
        .x( d => xScale( d.gameweek ))
        .y( d => yScale (d.league_position) + (yScale.bandwidth()/2) )
    )
    .attr('stroke', 
        function(d) {

            var gradient = defs.append("linearGradient")
            .attr("id", "league_position_gradient")
            .attr("x1", "0%")
            .attr("y1", "0%")
            .attr("x2", "0%")
            .attr("y2", "100%")

            gradient.append("stop")
            .attr("offset", "0%")
            .style("stop-color", colours_scale( d3.min( database['player_data'][manager_code]['season_performance']['league_position_array'] )))

            gradient.append("stop")
            .attr("offset", "100%")
            .style("stop-color", colours_scale( d3.max( database['player_data'][manager_code]['season_performance']['league_position_array'] )) )

            return 'url(#league_position_gradient)'


        })
    .style('stroke-width', 2)
    .attr('fill', 'transparent');


    var data_group = data_layer.selectAll('g')
    .data(dataset.filter(function(d) { return d.manager_code === manager_code }))
    .enter()
    .append('g')

    data_group.each( function(d) {

        d3.select(this).append('circle')
        .attr('cy', d => yScale(d.league_position) + (yScale.bandwidth()/2))
        .attr('cx', d => xScale(d.gameweek))
        .attr('r', 6)
        .style('fill', d => colours_scale(d.league_position))

    })



}