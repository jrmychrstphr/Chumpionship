function points_scored(manager_code) {

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
	            var overall_score = val['season_performance']['fixture_score_running_total_array'][idx]
	            var fixture_score = val['season_performance']['fixture_score_array'][idx]
	            var points_scored = val['season_performance']['points_scored_array'][idx]
	            var points_spent = val['season_performance']['points_spent_array'][idx]
	            var points_on_bench = val['season_performance']['points_on_bench_array'][idx]

	            temp_obj = {
	                'manager_code': key,
	                'gameweek': gameweek,
	                'total_overall_score': overall_score,
	                'fixture_score': fixture_score,
	                'points_scored': points_scored,
	                'points_spent': points_spent,
	                'points_on_bench': points_on_bench

	            }

	            dataset.push(temp_obj)
	        }

    })

    dataset = dataset.slice().sort((a, b) => d3.ascending(a.gameweek, b.gameweek))
    //console.log('points scored')
    //console.log(dataset)

    //Build dataviz -- score over time
    viz_div = $("#score-over-time .dynamic-content")

    dataviz_config = {
        'viz_height': viz_div.height(),
        'viz_width': viz_div.width(),
        'canvas_padding': {
            'top': 10,
            'right': 20,
            'bottom': 35,
            'left': 50
        }
    }


    var viz_container = d3.select("#score-over-time .dynamic-content")

    var svg = viz_container.append("svg")
    .attr('height', dataviz_config.viz_height)
    .attr('width', dataviz_config.viz_width);

    // define scales

    // xScale
    var xDomain = d3.extent(dataset, d => d.gameweek)

    var xScale = d3.scaleLinear()
    .domain(xDomain)
    .range([dataviz_config.canvas_padding.left, (dataviz_config.viz_width - dataviz_config.canvas_padding.right)]);

    //yScale
    var yDomain = function() {
        e = d3.extent(dataset, d => d.total_overall_score)

        //zero the axis
        if (e[0] > 0) {
            e[0] = 0
        }

        //

        return e
    } ()

    var yScale = d3.scaleLinear()
    .domain(yDomain)   
    .range([(dataviz_config.viz_height - dataviz_config.canvas_padding.bottom), dataviz_config.canvas_padding.top]);

    // background
    var background = svg.append('g')
    .classed('background', true)


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

        for (i = domain[0]; i <= domain[domain.length-1]; i++ ){

            if (i === domain[0] || i === domain[domain.length-1] && (domain[domain.length-1] % 10) > 2 || i % 10 === 0) { 
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
    
    var xAxisGridGenerator = xAxisGenerator
    .tickSize(dataviz_config.viz_height - dataviz_config.canvas_padding.bottom)
    .tickSizeOuter(0)
    .tickFormat("");

    var xAxisGrid = svg.append("g")
    .attr("class", "x axis-grid")
    .call(xAxisGridGenerator)
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
    yAxis.style('transform', 'translateX(35px)');

    //def
    var defs = svg.append("defs")

    var colours_scale = d3.scaleLinear()
    .domain(d3.extent(xDomain))
    .range([chump_colours.blue, chump_colours.green])
    .interpolate(d3.interpolateRgb);


    // data layer
    var data_layer = svg.append('g')
    .classed('data-layer', true)

    //create dataset for fill
    minmax_dataset = []
    for ( i = d3.min(dataset, d => d.gameweek); i <= d3.max(dataset, d => d.gameweek); i++ ) {
    	//console.log(i)

    	temp_obj = {
    		'gameweek': i,
    		'max': d3.max(dataset.filter(function(d) { return d.gameweek === i }), d => d.total_overall_score),
    		'min': d3.min(dataset.filter(function(d) { return d.gameweek === i }), d => d.total_overall_score)
    	}

    	minmax_dataset.push(temp_obj)
    }

    //console.log(minmax_dataset)


	// Add the area
    background.append("path")
	.datum(minmax_dataset)
	.attr("fill", chump_colours.dark_grey)
	//.attr("stroke", "#69b3a2")
	//.attr("stroke-width", 1.5)
	.attr("d", d3.area()
	.x(function(d) { return xScale( d.gameweek ) })
	.y0(function(d) { return yScale( d.min ) })
	.y1(function(d) { return yScale( d.max ) })
	)

	var data_path = data_layer.append('path')
    .datum(dataset.filter(function(d) { return d.manager_code === manager_code }))
    .attr("d", d3.line()
        .x( d => xScale(d.gameweek))
        .y( d => yScale (d.total_overall_score) )
    )
    .attr('stroke', function(d){

		var gradient = defs.append("linearGradient")
        .attr("id", "points_scored_gradient")
        .attr("x1", "0%")
        .attr("y1", "0%")
        .attr("x2", "0%")
        .attr("y2", "100%")

        gradient.append("stop")
        .attr("offset", "0%")
        .style("stop-color", colours_scale( d3.max( dataset, d => d.gameweek )))

        gradient.append("stop")
        .attr("offset", "100%")
        .style("stop-color", colours_scale( d3.min( dataset, d => d.gameweek )) )

        f = 'url(#points_scored_gradient)'

    	return f

    })
    .style('stroke-width', 2)
    //.style('opacity', 0.25)
    .attr('fill', 'transparent');

    var data_group = data_layer.selectAll('g')
    .data(dataset.filter(function(d) { return d.manager_code === manager_code }))
    .enter()
    .append('g')

    data_group.each( function(d) {

        d3.select(this).append('circle')
        .attr('cy', d => yScale(d.total_overall_score))
        .attr('cx', d => xScale(d.gameweek))
        .attr('r', 6)
        .style('fill', d => colours_scale(d.gameweek))

    })



    /* Points per gameweek */
    viz_div = $("#score-by-gameweek .dynamic-content")

    dataviz_config = {
        'viz_height': viz_div.height(),
        'viz_width': viz_div.width(),
        'canvas_padding': {
            'top': 10,
            'right': 20,
            'bottom': 35,
            'left': 50
        }
    }

    var viz_container = d3.select("#score-by-gameweek .dynamic-content")

    var svg = viz_container.append("svg")
    .attr('height', dataviz_config.viz_height)
    .attr('width', dataviz_config.viz_width);

    // define scales

    // xScale
    var xDomain = function(){

        function onlyUnique(value, index, self) { 
            return self.indexOf(value) === index;
        }

        temp_array = []

        $.each(dataset, function(){
            temp_array.push( this.gameweek )
        })

        var g = temp_array.filter( onlyUnique )

        //console.log(g)
        return g


    } ()

    var xScale = d3.scaleBand()
    .domain(xDomain)
    .range([dataviz_config.canvas_padding.left, (dataviz_config.viz_width - dataviz_config.canvas_padding.right)])
    .paddingInner(0.25)

    //yScale
    var yDomain = function() {
        e = d3.extent(dataset, d => d.fixture_score)

        //zero the axis
        if (e[0] > 0) {
            e[0] = 0
        }

        console.log(e)
        return e
    } ()

    var yScale = d3.scaleLinear()
    .domain(yDomain)   
    .range([(dataviz_config.viz_height - dataviz_config.canvas_padding.bottom), dataviz_config.canvas_padding.top]);

    //def
    var defs = svg.append("defs")

    var colours_scale = d3.scaleLinear()
    .domain(d3.extent(yDomain))
    .range([chump_colours.blue, chump_colours.green])
    .interpolate(d3.interpolateRgb);

    //add 'max score' in background
    var background = svg.append('g')
    .classed('background', true)

    max_dataset = function() {

        temp_array = []

        $.each( xDomain, function(idx, val){

            //console.log(val)
            max = d3.max(dataset.filter( function(d) { return d.gameweek === val }), d => d.fixture_score)
            //console.log(max)

            temp_obj = {
                'gameweek': val,
                'max_score': max
            }

            temp_array.push(temp_obj)

        } )

        //console.log(temp_array)
        return temp_array

    } ()

    var max_score_bars = background.selectAll('.bar')
    .data(max_dataset)
    .enter()
    .append('rect')
    .classed('bar', true)
    .attr("y", function(d) { return yScale(d.max_score) })
    .attr("height", function(d) { return yScale(0) - yScale(d.max_score) })
    .attr("x", function(d) { return xScale(d.gameweek); })
    .attr("width", xScale.bandwidth())
    .style("fill", chump_colours.dark_grey)

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

        for (i = domain[0]; i <= domain[domain.length-1]; i++ ){

            if (i === domain[0] || i === domain[domain.length-1] && (domain[domain.length-1] % 10) > 2 || i % 10 === 0) { 
                temp_array.push(i)
             }
        }

        return temp_array

    } ())
    .tickFormat(d => ("GW" + d));
    
    var xAxis = svg.append("g")
    .classed("x axis", true)
    .call(xAxisGenerator);

    xAxis.select(".domain").remove();
    xAxis.attr('transform', function(d) {
            return 'translate(0 ' + (dataviz_config.viz_height - dataviz_config.canvas_padding.bottom) + ')';
        });

    //yAxis
    var yAxisGenerator = d3.axisLeft(yScale)
    .tickSizeOuter(0)
    .tickSize(0)

    var yAxis = svg.append("g")
    .classed("y axis", true)
    .call(yAxisGenerator);

    var yAxisGridGenerator = yAxisGenerator
    .tickSize(-dataviz_config.viz_width)
    .tickSizeOuter(0)
    .tickFormat("");

    var yAxisGrid = svg.append("g")
    .attr("class", "y axis-grid")
    .call(yAxisGridGenerator)
    .select(".domain").remove();


    yAxis.select(".domain").remove();
    yAxis.selectAll(".tick text").attr('dy', '0.3em');
    yAxis.style('transform', 'translateX(35px)');


    //add data
    var data_layer = svg.append('g')
    .classed('data_layer', true)

    var data_bars = data_layer.selectAll('.bar')
    .data(dataset.filter(function(d) { return d.manager_code === manager_code }))
    .enter()
    .append('rect')
    .classed('bar', true)
    .attr("y", function(d) { return yScale(d.fixture_score) })
    .attr("height", function(d) { return yScale(0) - yScale(d.fixture_score) })
    .attr("x", function(d) { return xScale(d.gameweek); })
    .attr("width", xScale.bandwidth())
    .style("fill", chump_colours.grey)

}