$('document').ready(function(){
    let img = document.getElementById("tree_img");
    img.src="";

    $.post('/compile', csv => {
        var parsedCSV = d3.csv.parseRows(csv);
        d3.select("table")

            .selectAll("tr")
                .data(parsedCSV).enter()
                .append("tr")

            .selectAll("td")
                .data(function(d) { return d; }).enter()
                .append("td")
                .text(function(d) { return d; });
            
    }).then(() => {
        img.src = "/tree_img" // + new Date().getTime();
    })
});