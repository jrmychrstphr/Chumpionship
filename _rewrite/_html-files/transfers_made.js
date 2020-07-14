function transfers_made(manager_code) {

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
	            var points_spent = val['season_performance']['points_spent_array'][idx]
                var transfers_made = val['season_performance']['transfers_made_array'][idx]

	            temp_obj = {
	                'manager_code': key,
	                'gameweek': gameweek,
                    'points_spent': points_spent,
	                'transfers_made': transfers_made
	            }

	            dataset.push(temp_obj)
	        }

    })

    dataset = dataset.slice().sort((a, b) => d3.ascending(a.gameweek, b.gameweek))
    console.log(dataset)

    // add big numbers
    d3.select('#total-transfers div.dynamic-content')
    .text(d3.sum(dataset.filter(function(d) { return d.manager_code === manager_code }), d => d.transfers_made) )

    d3.select('#total-points-spent div.dynamic-content')
    .text(d3.sum(dataset.filter(function(d) { return d.manager_code === manager_code }), d => d.points_spent) )





    //Build dataviz -- score over time
    viz_div = $("#transfers-by-gameweek .dynamic-content")

    viz_div.css("height", function() {
        h = 10+35+(d3.max(dataset, d => d.transfers_made)*9)
        return h
    })

    dataviz_config = {
        'viz_height': viz_div.height(),
        'viz_width': viz_div.width(),
        'canvas_padding': {
            'top': 10,
            'right': 15,
            'bottom': 35,
            'left': 15
        }
    }


    var viz_container = d3.select("#transfers-by-gameweek .dynamic-content")

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
        e = d3.extent(dataset, d => d.transfers_made)

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


    // colour scales
    var colours_scale_x = d3.scaleLinear()
    .domain(d3.extent(xDomain))
    .range([chump_colours.blue, chump_colours.green])
    .interpolate(d3.interpolateRgb);

    var colours_scale_y = d3.scaleLinear()
    .domain(d3.extent(yDomain))
    .range([chump_colours.blue, chump_colours.green])
    .interpolate(d3.interpolateRgb);


    var colours_scale_data = d3.scaleLinear()
    .domain(d3.extent(dataset.filter(function(d) { return d.manager_code === manager_code && d.transfers_made > 0 }), d => d.transfers_made))
    .range([chump_colours.blue, chump_colours.green])
    .interpolate(d3.interpolateRgb);


    // background
    var background = svg.append('g')
    .classed('background', true)

    max_dataset = function() {

        temp_array = []

        $.each( xDomain, function(idx, val){

            max = d3.max(dataset.filter( function(d) { return d.gameweek === val }), d => d.transfers_made)

            temp_obj = {
                'gameweek': val,
                'max': max
            }

            temp_array.push(temp_obj)

        } )

        //console.log(temp_array)
        return temp_array

    } ()

    var max_group = background.selectAll('g')
    .data(max_dataset)
    .enter()
    .append('g')

    max_group.each( function(d) {

        for (i = 0; i < d.max; i++) {

            d3.select(this).append('circle')
            .attr('cy', d => yScale(i+1) )
            .attr('cx', d => xScale(d.gameweek) + xScale.bandwidth()*0.5 )
            .attr('r', 3.5)
            .style('fill', chump_colours.dark_grey)

        }


    })


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
    
    //yAxis
    var yAxisGenerator = d3.axisLeft(yScale)
    .tickSizeOuter(0)
    .tickSize(0)
    .tickValues([]);

    var yAxis = svg.append("g")
    .classed("y axis", true)
    .call(yAxisGenerator);

    yAxis.select(".domain").remove();
    yAxis.selectAll(".tick text").attr('dy', '0.3em');
    yAxis.style('transform', 'translateX(35px)');

    var yAxisGridGenerator = yAxisGenerator
    .tickSize(-dataviz_config.viz_width)
    .tickSizeOuter(0)
    .tickFormat("")
    .tickValues([0]);

    var yAxisGrid = svg.append("g")
    .attr("class", "y axis-grid")
    .call(yAxisGridGenerator)
    .select(".domain").remove();


    //add data
    var data_layer = svg.append('g')
    .classed('data_layer', true)

    var data_group = data_layer.selectAll('g')
    .data(dataset.filter(function(d) { return d.manager_code === manager_code }))
    .enter()
    .append('g')

    data_group.each( function(d) {

        for (i = 0; i < d.transfers_made; i++) {

            d3.select(this).append('circle')
            .attr('cy', d => yScale(i+1) )
            .attr('cx', d => xScale(d.gameweek) + xScale.bandwidth()*0.5 )
            .attr('r', 3.5)
            .style("fill", function(d) {
                e = d3.extent(dataset.filter(function(d) { return d.manager_code === manager_code && d.transfers_made > 0 }), d => d.transfers_made)

                if ( d.transfers_made === e[0] || d.transfers_made === e[1] ) {
                    f = colours_scale_data(d.transfers_made)
                } else {
                    f = chump_colours.grey
                }

                return f
            })


        }


    })

/*

    var data_bars = data_layer.selectAll('.bar')
    .data(dataset.filter(function(d) { return d.manager_code === manager_code }))
    .enter()
    .append('rect')
    .classed('bar', true)
    .attr("y", function(d) { return yScale(d.transfers_made) })
    .attr("height", function(d) { return yScale(0) - yScale(d.transfers_made) })
    .attr("x", function(d) { return xScale(d.gameweek); })
    .attr("width", xScale.bandwidth())
    .style("fill", chump_colours.grey)

*/
}