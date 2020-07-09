$('document').ready(function(){
    let img = document.getElementById("tree_img");
    let pdf_viewer = document.getElementById("pdf_viewer");
    pdf_viewer.data="";

    //compile(25, true);
});

function compile(reset) {
    let label = document.getElementById("msg");

    let qtyInput = document.getElementById("qtyInput");
    let amount = parseInt(qtyInput.value)
    if (isNaN(amount)) {
        label.innerText = "Invalid input : please enter a number";
        return;
    }
    if (amount < 1 || amount > 100) {
        label.innerText = "Invalide input : please enter a number of documents between 1 and 100";
        return;
    }
    // else


    label.innerText = (reset ? "Generating" : "Adding" ) + " " + amount + " documents";

    route = '/compile/' + amount;
    if (reset) {
        document.getElementsByClassName("table-container")[0].style["visibility"] = "hidden";
        document.getElementsByTagName("thead")[0].innerHTML = "";
        document.getElementsByTagName("tbody")[0].innerHTML = "";
    }
    else route += "/False"

    $.post(route, csv => {
        var parsedCSV = d3.csv.parseRows(csv);
        if (reset)
            d3.select("thead")
                .selectAll("th")
                    .data(parsedCSV[0]).enter()
                    .append("th")
                    .text(d => d)

        let new_rows = d3.select("tbody")
            .selectAll("tr")
            .data(d3.csv.parse(csv))
            .enter()
            .append("tr")
        new_rows.selectAll("td")
                    .data(function(d) { return Object.values(d); }).enter()
                    .append("td")
                    .text(function(d) { return d; });
        
        new_rows.append("td")
                .append("button")
                .text("PDF")
                .on("click", build_pdf)
        
        document.getElementsByClassName("table-container")[0].style["visibility"] = "visible";
        document.getElementById("addBtn").disabled = false;

        label.innerText = "";
    })
}

function build_pdf(data) {
    delete data[""]
    let pdf_viewer = document.getElementById("pdf_viewer");
    pdf_viewer.data = "";
    $.post('/build_pdf', data).then(()=>{
        pdf_viewer.data = "/build_pdf"
    })
}
