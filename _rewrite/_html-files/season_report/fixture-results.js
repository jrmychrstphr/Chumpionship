function fixture_results(manager_code) {


    if (!(manager_code)) {
        manager_code = '55259'
    }
    // Compile a dataset from the database
    var dataset = []

    $.each( database['player_data'], function(key, val) {

            $.each( val.gw_performance, function(k,v) {

                gameweek = k
                score = v.fixture_score
                result = v.fixture_result
                opponent_team_name = v.fixture_opponent_team_name
                opponent_score = return_fixture_score(database, v.fixture_opponent_manager_code, gameweek)

                temp_obj = {
                    'manager_code': key,
                    'gameweek': parseInt(gameweek),
                    'score': score,
                    'result': result,
                    'opponent_team_name': opponent_team_name,
                    'opponent_score': opponent_score,
                    'margin': score - opponent_score

                }

                dataset.push(temp_obj)
            } )

        dataset = dataset.slice().sort((a, b) => d3.ascending(a.gameweek, b.gameweek))

    });

    //console.log(dataset)

    $("#fixture-results .dynamic-content").empty()

    var viz_container = d3.select("#fixture-results .dynamic-content")
    .classed('grid-container two-cols', true)

    fixtures = dataset.filter(function(d) { return d.manager_code === manager_code }).slice().sort((a, b) => d3.ascending(a.gameweek, b.gameweek))

    $.each(fixtures, function(i) {

        d = this

        if ( i === 0 ) {
            //console.log(i)
            column = viz_container.append('div').classed('grid-item col-1', true)
        } else if ( i === Math.ceil(fixtures.length/2) ) { 
            //console.log(i)
            column = viz_container.append('div').classed('grid-item col-2', true)
        }

        var row = column.append('div').classed('table-row', true)
        .style('border-color', chump_colours.dark_grey)

        // gameweek
        row.append('div')
        .classed('table-column', true)
        .text( "GW" + d.gameweek )

        // score
        row.append('div')
        .classed('table-column', true)
        .text( function() {

            s = d.score
            o = d.opponent_score

            text = s + " – " + o

            return text

        } )

        // result
        row.append('div')
        .classed('table-column', true)
        .classed('result', true)
        .text( function() {

            r = d.result

            if ( r === "D" ) {
                text = "Draw"
            } else if ( r === "W" ) {
                text = "Win"
            } else if ( r === "L" ) {
                text = "Loss"
            } else {
                text = "Err"
            }

            return text
        } )
        .style('border-color', function() {

            r = d.result

            if ( r === "D" ) {
                f = chump_colours.grey
            } else if ( r === "W" ) {
                f = chump_colours.green
            } else if ( r === "L" ) {
                f = chump_colours.blue
            } else {
                f = 'black'
            }

            return f
        })


        // opponent
        row.append('div')
        .classed('table-column', true)
        .text( function() {
            o = d.opponent_team_name
            text = 'vs ' + o

            return text
        } )
    })


    /* streaks */
    
    streaks_dataset = []     

    //for each player in the database
    $.each( database['player_data'], function(key, val) {


        gameweeks_played = return_gameweeks_played(database)
        temp_results = []
        temp_streaks = []

        // for each gameweek
        for ( idx = 0; idx < gameweeks_played; idx++ ) {
            var gameweek = idx+1
            var result = val['season_performance']['result_array'][idx]

            temp_obj = {
                'gameweek': gameweek,
                'result': result
            }

            temp_results.push(temp_obj)
        }

        //console.log(temp_results)


        $.each ( temp_results.slice().sort((a, b) => d3.ascending(a.gameweek, b.gameweek)), function(idx, val) {

            console.log("idx:"+idx)
            //console.log(val)

            if ( val.result === 'W' ) {
                streak_type = 'win'
            } else {
                streak_type = 'winless'
            }

            function create_new() {
                new_obj = {}
                new_obj.streak_start = val.gameweek
                new_obj.streak_type = streak_type
                new_obj.current_streak = true
                new_obj.manager_code = key
                new_obj.manager_name = return_manager_fullname(database, key)

                return new_obj
            }


            // if it's the first result...
            if (temp_streaks.length === 0 ) {

                //... push a new streak obj to the array
                temp_streaks.push(create_new())

            } else {

                // copy the latest streak obj to compare
                prev_obj = temp_streaks[temp_streaks.length-1]

                // if the current streak ends...
                if ( prev_obj.streak_type != streak_type ) {
                    //... mark the current streak status to false
                    temp_streaks[temp_streaks.length-1].current_streak = false
                    //... end the previous streak in previous gameweek
                    temp_streaks[temp_streaks.length-1].streak_end = val.gameweek-1

                    //... and add a new streak object
                    temp_streaks.push(create_new())

                // if this is the final fixture...    
                } else if ( idx === gameweeks_played-1 ) {
                    //... end the streak
                    temp_streaks[temp_streaks.length-1].streak_end = val.gameweek                      
                }
            }


        })

        $.each( temp_streaks, function() {
            this.streak_length = (this.streak_end - this.streak_start) + 1
            streaks_dataset.push(this) 
        } );
        
    })

    console.log(streaks_dataset)

    //Build dataviz -- longest win streaks
    viz_div = $("#longest-win-streak .dynamic-content").empty()

    dataviz_config = {
        'viz_height': viz_div.height(),
        'viz_width': viz_div.width(),
        'canvas_padding': {
            'top': 30,
            'right': 10,
            'bottom': 10,
            'left': 10
        }
    }


    var viz_container = d3.select("#longest-win-streak .dynamic-content")

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

    var xScale = d3.scaleLinear()
    .domain(d3.extent(xDomain))
    .range([dataviz_config.canvas_padding.left, (dataviz_config.viz_width - dataviz_config.canvas_padding.right)])

    //yScale
    var yDomain = [manager_code]

    var yScale = d3.scaleBand()
    .domain(yDomain)
    .range([(dataviz_config.viz_height - dataviz_config.canvas_padding.bottom), dataviz_config.canvas_padding.top]);


    //add data
    var data_layer = svg.append('g')
    .classed('data_layer', true)

    var data_rings = data_layer.selectAll('.ring')
    .data(dataset.filter(function(d) { return d.manager_code === manager_code }))
    .enter()
    .append('circle')
    .classed('ring', true)
    .attr("cy", function(d) { 
        return yScale(d.manager_code)  + yScale.bandwidth()*0.5
    })
    .attr("cx", function(d) { return xScale(d.gameweek); })
    .attr("r", 6)
    .style("fill", function(d) {

            if (d.result === 'D') {
                f = chump_colours.grey
            } else if (d.result === 'W') {
                f = chump_colours.green
            } else if (d.result === 'L') {
                f = chump_colours.blue
            } else {
                f = 'Black'
            }      

            return f

    })
    .style('opacity', 0.35)

    var longest_length = d3.max(streaks_dataset.filter(function(d) { return d.manager_code === manager_code && d.streak_type === "win"}), d => d.streak_length)

    var longest_streaks_array = streaks_dataset.filter(function(d) { 
        return d.manager_code === manager_code && d.streak_type === "win" && d.streak_length === longest_length
    })

    longest_streaks_dataset = []

    $.each( longest_streaks_array, function(k, v) {
        for (i = v.streak_start; i <= v.streak_end; i++) {
            temp_obj = {
                'gameweek': i,
                'manager_code': v.manager_code
            }

            longest_streaks_dataset.push(temp_obj)
        }
    })

    var data_line = data_layer.selectAll('line')
    .data(longest_streaks_array)
    .enter()
    .append('line')
    .attr('x1', function(d) { 
        return xScale(d.streak_start)
    })
    .attr('x2', function(d) { 
        return xScale(d.streak_end)
    })
    .attr('y1', function(d) { 
        return yScale(d.manager_code)  + yScale.bandwidth()*0.5
    })
    .attr('y2', function(d) { 
        return yScale(d.manager_code)  + yScale.bandwidth()*0.5
    })
    .style('stroke', chump_colours.green)
    .style('stroke-width', 3)

    var data_dots = data_layer.selectAll('.dot')
    .data(longest_streaks_dataset)
    .enter()
    .append('circle')
    .classed('dot', true)
    .attr("cy", function(d) { 
        return yScale(d.manager_code)  + yScale.bandwidth()*0.5
    })
    .attr("cx", function(d) { return xScale(d.gameweek); })
    .attr("r", 6)
    .style("fill", chump_colours.green )
    .style('stroke', 'black')


    data_line.each( function(d) {

        // add 'n fixtures' above streak
        var streak_length = data_layer.append('text')
        .text(d.streak_length)
        .attr('x', xScale( d.streak_start + ((d.streak_length-1)/2) ))
        .attr('y', yScale(d.manager_code) + yScale.bandwidth()*0.5 )
        .attr('dy', '-0.5em')
        .style('fill', 'white')
        .style('font-size', '2rem')
        .style('font-family', 'champion')
        .style('font-weight', '600')
        .style('text-anchor', 'middle')

        // add 'GW0-0' below streak
        var streak_length = data_layer.append('text')
        .text("GWs " + d.streak_start + "–" + d.streak_end)
        .attr('x', xScale( d.streak_start + ((d.streak_length-1)/2) ))
        .attr('y', yScale(d.manager_code) + yScale.bandwidth()*0.5 )
        .attr('dy', '2em')
        .style('fill', chump_colours.grey)
        //.style('font-size', '1rem')
        .style('text-anchor', 'middle')


    })


    //Build dataviz -- longest win streaks
    viz_div = $("#longest-winless-streak .dynamic-content").empty()

    dataviz_config = {
        'viz_height': viz_div.height(),
        'viz_width': viz_div.width(),
        'canvas_padding': {
            'top': 30,
            'right': 10,
            'bottom': 10,
            'left': 10
        }
    }


    var viz_container = d3.select("#longest-winless-streak .dynamic-content")

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

    var xScale = d3.scaleLinear()
    .domain(d3.extent(xDomain))
    .range([dataviz_config.canvas_padding.left, (dataviz_config.viz_width - dataviz_config.canvas_padding.right)])

    //yScale
    var yDomain = [manager_code]

    var yScale = d3.scaleBand()
    .domain(yDomain)
    .range([(dataviz_config.viz_height - dataviz_config.canvas_padding.bottom), dataviz_config.canvas_padding.top]);


    //add data
    var data_layer = svg.append('g')
    .classed('data_layer', true)

    var data_rings = data_layer.selectAll('.ring')
    .data(dataset.filter(function(d) { return d.manager_code === manager_code }))
    .enter()
    .append('circle')
    .classed('ring', true)
    .attr("cy", function(d) { 
        return yScale(d.manager_code)  + yScale.bandwidth()*0.5
    })
    .attr("cx", function(d) { return xScale(d.gameweek); })
    .attr("r", 6)
    .style("fill", function(d) {

            if (d.result === 'D') {
                f = chump_colours.grey
            } else if (d.result === 'W') {
                f = chump_colours.green
            } else if (d.result === 'L') {
                f = chump_colours.blue
            } else {
                f = 'Black'
            }      

            return f

    })
    .style('opacity', 0.35)

    var longest_length = d3.max(streaks_dataset.filter(function(d) { return d.manager_code === manager_code && d.streak_type === "winless"}), d => d.streak_length)

    var longest_streaks_array = streaks_dataset.filter(function(d) { 
        return d.manager_code === manager_code && d.streak_type === "winless" && d.streak_length === longest_length
    })

    longest_streaks_dataset = []

    $.each( longest_streaks_array, function(k, v) {
        for (i = v.streak_start; i <= v.streak_end; i++) {
            temp_obj = {
                'gameweek': i,
                'manager_code': v.manager_code
            }

            longest_streaks_dataset.push(temp_obj)
        }
    })

    var data_line = data_layer.selectAll('line')
    .data(longest_streaks_array)
    .enter()
    .append('line')
    .attr('x1', function(d) { 
        return xScale(d.streak_start)
    })
    .attr('x2', function(d) { 
        return xScale(d.streak_end)
    })
    .attr('y1', function(d) { 
        return yScale(d.manager_code)  + yScale.bandwidth()*0.5
    })
    .attr('y2', function(d) { 
        return yScale(d.manager_code)  + yScale.bandwidth()*0.5
    })
    .style('stroke', chump_colours.blue)
    .style('stroke-width', 3)

    var data_dots = data_layer.selectAll('.dot')
    .data(longest_streaks_dataset)
    .enter()
    .append('circle')
    .classed('dot', true)
    .attr("cy", function(d) { 
        return yScale(d.manager_code)  + yScale.bandwidth()*0.5
    })
    .attr("cx", function(d) { return xScale(d.gameweek); })
    .attr("r", 6)
    .style("fill", function(d, i) {

        var g = d.gameweek

        var r = dataset.filter(function(d) { return d.manager_code === manager_code && d.gameweek === g})[0].result
        //console.log(g)
        //console.log(r)

        if ( r === 'L' ) {
            f = chump_colours.blue
        } else if ( r === 'D' ) {
            f = chump_colours.grey
        } else {
            f = 'white'
        }

        return f
    } )
    .style('stroke', 'black')


    data_line.each( function(d) {

        // add 'n fixtures' above streak
        var streak_length = data_layer.append('text')
        .text(d.streak_length)
        .attr('x', xScale( d.streak_start + ((d.streak_length-1)/2) ))
        .attr('y', yScale(d.manager_code) + yScale.bandwidth()*0.5 )
        .attr('dy', '-0.5em')
        .style('fill', 'white')
        .style('font-size', '2rem')
        .style('font-family', 'champion')
        .style('font-weight', '600')
        .style('text-anchor', 'middle')

        // add 'GW0-0' below streak
        var streak_length = data_layer.append('text')
        .text("GWs " + d.streak_start + "–" + d.streak_end)
        .attr('x', xScale( d.streak_start + ((d.streak_length-1)/2) ))
        .attr('y', yScale(d.manager_code) + yScale.bandwidth()*0.5 )
        .attr('dy', '2em')
        .style('fill', chump_colours.grey)
        //.style('font-size', '1rem')
        .style('text-anchor', 'middle')


    })

    /* Biggest results */

    //Build dataviz -- largest win
    dataset_largest_wins = dataset.filter(function(d) { return d.manager_code === manager_code && d.margin === d3.max(dataset.filter(function(d) { return d.manager_code === manager_code }), d => d.margin  ) })
    
    viz_div = $("#largest-win .dynamic-content")
    viz_div.css('height', function(d) {
        return (dataset_largest_wins.length * 100)
    })


    dataviz_config = {
        'viz_height': viz_div.height(),
        'viz_width': viz_div.width(),
        'canvas_padding': {
            'top': 20,
            'right': 10,
            'bottom': 35,
            'left': 10
        }
    }

    $("#largest-win .dynamic-content").empty()
    var viz_container = d3.select("#largest-win .dynamic-content")

    var svg = viz_container.append("svg")
    .attr('height', dataviz_config.viz_height)
    .attr('width', dataviz_config.viz_width);

    // define scales
    // xScale
    var xDomain = function(){

        e = d3.extent(dataset, d => d.score)

        //zero the axis
        if (e[0] > 0) {
            e[0] = 0
        } else {
            e[0] = Math.ceil(e[0] / 25) * 25;
        }

        e[1] = Math.ceil(e[1] / 25) * 25;

        //console.log(e)
        return e


    } ()

    var xScale = d3.scaleLinear()
    .domain(d3.extent(xDomain))
    .range([dataviz_config.canvas_padding.left, (dataviz_config.viz_width - dataviz_config.canvas_padding.right)])

    //yScale
    var yDomain = function() {
        temp = []
        $.each( dataset_largest_wins, function(i) {
            temp.push(i)
        } )
        //console.log(temp)
        return temp
    } ()

    var yScale = d3.scaleBand()
    .domain(yDomain)
    .range([(dataviz_config.viz_height - dataviz_config.canvas_padding.bottom), dataviz_config.canvas_padding.top])
    .paddingInner(.25)


    //xAxis
    var xAxisGenerator = d3.axisBottom(xScale)
    .tickSizeOuter(0)
    .tickSize(10)
    .tickPadding(10)
    .tickValues(function() {
        
        var temp_array = [];
        var d = xDomain

        var interval = 25

        for (i = d[0]; i <= d[d.length-1]; i++ ){

            if (i % interval === 0) { 
                temp_array.push(i)
             }
        }

        return temp_array

    } ());

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

    //add data
    var data_layer = svg.append('g')
    .classed('data_layer', true)

    var data_groups = data_layer.selectAll('g')
    .data( dataset_largest_wins )
    .enter()
    .append('g')

    data_groups.each( function(d, i) {

        var line = d3.select( this )
        .append('line')
        .attr('x1', d => xScale(d.score))
        .attr('x2', d => xScale(d.opponent_score))
        .attr('y1', yScale(i) + yScale.bandwidth()*0.5 )
        .attr('y2', yScale(i) + yScale.bandwidth()*0.5 )
        .style('stroke-width', 2)
        .style('stroke', chump_colours.green)

        var score_dot = d3.select( this )
        .append('circle')
        .attr('cy', yScale(i) + yScale.bandwidth()*0.5 )
        .attr('cx', d => xScale(d.score))
        .attr('r', 6)
        .style('fill', chump_colours.green)
        .style('stroke', chump_colours.green)
        .style('stroke-width', 2)

        var opp_dot = d3.select( this )
        .append('circle')
        .attr('cy', yScale(i) + yScale.bandwidth()*0.5 )
        .attr('cx', d => xScale(d.opponent_score))
        .attr('r', 6)
        .style('fill', 'black')
        .style('stroke', chump_colours.green)
        .style('stroke-width', 2)

        // add 'n fixtures' above streak
        var margin = data_layer.append('text')
        .text("+"+d.margin)
        .attr('x', xScale( d.opponent_score + ((d.margin-1)/2) ))
        .attr('y', yScale(i) + yScale.bandwidth()*0.5 )
        .attr('dy', '-0.3em')
        .style('fill', 'white')
        .style('font-size', '2rem')
        .style('font-family', 'champion')
        .style('font-weight', '600')
        .style('text-anchor', 'middle')

        // add 'GW0-0' below streak
        var streak_length = data_layer.append('text')
        .text(" vs " + d.opponent_team_name + ", GW" + d.gameweek )
        .attr('x', xScale( d.opponent_score + ((d.margin-1)/2) ))
        .attr('y', yScale(i) + yScale.bandwidth()*0.5 )
        .attr('dy', '2em')
        .style('fill', 'white')
        //.style('font-size', '1rem')
        .style('text-anchor', 'middle')


    })

    //Build dataviz -- largest defeat
    dataset_largest_defeats = dataset.filter(function(d) { return d.manager_code === manager_code && d.margin === d3.min(dataset.filter(function(d) { return d.manager_code === manager_code }), d => d.margin  ) })
    
    viz_div = $("#largest-defeat .dynamic-content")
    viz_div.css('height', function(d) {
        return (dataset_largest_wins.length * 100)
    })


    dataviz_config = {
        'viz_height': viz_div.height(),
        'viz_width': viz_div.width(),
        'canvas_padding': {
            'top': 20,
            'right': 10,
            'bottom': 35,
            'left': 10
        }
    }

    $("#largest-defeat .dynamic-content").empty()
    var viz_container = d3.select("#largest-defeat .dynamic-content")

    var svg = viz_container.append("svg")
    .attr('height', dataviz_config.viz_height)
    .attr('width', dataviz_config.viz_width);

    //yScale
    var yDomain = function() {
        temp = []
        $.each( dataset_largest_defeats, function(i) {
            temp.push(i)
        } )
        //console.log(temp)
        return temp
    } ()

    var yScale = d3.scaleBand()
    .domain(yDomain)
    .range([(dataviz_config.viz_height - dataviz_config.canvas_padding.bottom), dataviz_config.canvas_padding.top])
    .paddingInner(.25)


    //xAxis
    var xAxisGenerator = d3.axisBottom(xScale)
    .tickSizeOuter(0)
    .tickSize(10)
    .tickPadding(10)
    .tickValues(function() {
        
        var temp_array = [];
        var d = xDomain

        var interval = 25

        for (i = d[0]; i <= d[d.length-1]; i++ ){

            if (i % interval === 0) { 
                temp_array.push(i)
             }
        }

        return temp_array

    } ());

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

    //add data
    var data_layer = svg.append('g')
    .classed('data_layer', true)

    var data_groups = data_layer.selectAll('g')
    .data( dataset_largest_defeats )
    .enter()
    .append('g')

    data_groups.each( function(d, i) {

        var line = d3.select( this )
        .append('line')
        .attr('x1', d => xScale(d.score))
        .attr('x2', d => xScale(d.opponent_score))
        .attr('y1', yScale(i) + yScale.bandwidth()*0.5 )
        .attr('y2', yScale(i) + yScale.bandwidth()*0.5 )
        .style('stroke-width', 2)
        .style('stroke', chump_colours.blue)

        var score_dot = d3.select( this )
        .append('circle')
        .attr('cy', yScale(i) + yScale.bandwidth()*0.5 )
        .attr('cx', d => xScale(d.score))
        .attr('r', 6)
        .style('fill', chump_colours.blue)
        .style('stroke', chump_colours.blue)
        .style('stroke-width', 2)

        var opp_dot = d3.select( this )
        .append('circle')
        .attr('cy', yScale(i) + yScale.bandwidth()*0.5 )
        .attr('cx', d => xScale(d.opponent_score))
        .attr('r', 6)
        .style('fill', 'black')
        .style('stroke', chump_colours.blue)
        .style('stroke-width', 2)

        // add 'n fixtures' above streak
        var margin = data_layer.append('text')
        .text(d.margin)
        .attr('x', xScale( d.opponent_score + ((d.margin-1)/2) ))
        .attr('y', yScale(i) + yScale.bandwidth()*0.5 )
        .attr('dy', '-0.3em')
        .style('fill', 'white')
        .style('font-size', '2rem')
        .style('font-family', 'champion')
        .style('font-weight', '600')
        .style('text-anchor', 'middle')

        // add 'GW0-0' below streak
        var streak_length = data_layer.append('text')
        .text(" vs " + d.opponent_team_name + ", GW" + d.gameweek )
        .attr('x', xScale( d.opponent_score + ((d.margin-1)/2) ))
        .attr('y', yScale(i) + yScale.bandwidth()*0.5 )
        .attr('dy', '2em')
        .style('fill', 'white')
        //.style('font-size', '1rem')
        .style('text-anchor', 'middle')


    })




}