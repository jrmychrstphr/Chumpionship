<script>
    function return_gameweek_string(gameweek) {
        g = (("0" + parseInt(gameweek)).slice(-2) ).toString();
        return g
    }

    function return_ordinal(num) {
        var j = num % 10, k = num % 100;
        if (j == 1 && k != 11) { return num + "st"; }
        if (j == 2 && k != 12) { return num + "nd"; }
        if (j == 3 && k != 13) { return num + "rd"; }
        return num + "th";
    }

    function return_comma_formatted_number(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }

    function return_replace_diacritics(s) {

        s = s.normalize("NFD").replace(/[\u0300-\u036f]/g, "")
        return s;
    }
</script>