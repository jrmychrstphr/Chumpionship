/*
List of functions used across multiple files:

	* resize_rows(selector)

	* return_manager_code_array(input_database)
	* return_manager_fullname(input_database, manager_code)
	* return_gameweeks_played(input_database)

	* return_comma_formatted_number(num)
*/


function return_comma_formatted_number(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function return_manager_code_array(input_database) {
        
    array = [];
    player_data = input_database['player_data']

    Object.keys(player_data).forEach(function(k){
        array.push(k);
    });

    return array
}

function return_manager_fullname(input_database, manager_code) {
    fullname = input_database.player_data[manager_code].manager_info.manager_fullname
    return fullname
}

function resize_rows(selector) {

    $( selector ).each( function() {

        //console.log(this)

        cell_width_array = []

        $(this).find( "div.table-row" ).each(function() {

            $( this ).children().each(  function( idx ) {
                $(this).removeAttr('width')

                // if this is the first loop, the array will be shorter than idx+1
                if (cell_width_array.length < idx+1 ) {
                    // if so, add an array to hold the width vals of 
                    // *all* cells in that idx (same col) across all rowws
                    cell_width_array[idx] = []
                }

                // push the width of this cell to the array for this column
                cell_width = Number($( this ).width())
                cell_width_array[idx].push(cell_width)

            })

        });

        // set each cell's width to the longest in that column
        $(this).find( "div.table-row" ).each(function() {
            $( this ).children().each(  function(idx) {
                $(this).width(Math.max(...cell_width_array[idx]));
            })
        });

    })

}

function return_gameweeks_played(input_database) {

    m = return_manager_code_array(input_database)
    return parseInt(Object.keys(database['player_data'][m[0]]['gw_performance']).length)

}


