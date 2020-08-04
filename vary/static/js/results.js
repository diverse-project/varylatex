const CONFIG = Object();
let PROBAS = Object();

const RED = "#ff2020";
const GREEN = "#20ff20";

const enum_selects = [];
const bool_selects = [];
const choice_selects = [];
const number_divs = {};

$('document').ready(function(){
    let img = document.getElementById("tree_img");
    let pdf_viewer = document.getElementById("pdf_viewer");
    pdf_viewer.data="";

    fetch_congig_src();
});

function compile(reset) {
    let label = document.getElementById("msg");
    let table = document.getElementById("results");

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
        table.getElementsByTagName("thead")[0].innerHTML = "";
        table.getElementsByTagName("tbody")[0].innerHTML = "";
    }

    $.post(route, {'reset' : reset} ,csv => {
        let parsedCSV = d3.csv.parseRows(csv);
        let table = d3.select("#results");
        if (reset)
            table.select("thead")
                .selectAll("th")
                    .data(parsedCSV[0]).enter()
                    .append("th")
                    .text(d => d)

        let new_rows = table.select("tbody")
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
                .on("click", build_pdf);
        
        document.getElementsByClassName("table-container")[0].style["visibility"] = "visible";
        document.getElementById("addBtn").disabled = false;

        label.innerText = "";
    }).then(refresh_probas)
}

function build_pdf(data) {
    delete data[""]
    let pdf_viewer = document.getElementById("pdf_viewer");
    pdf_viewer.data = "";
    $.post('/build_pdf', data).then(()=>{
        pdf_viewer.data = "/build_pdf"
    })
}

function fetch_congig_src() {
    $.get("/config_src", load_config_src);
}

function load_config_src(cfgsrc) {
    table = document.getElementById("gen-table");
    tbody = document.createElement("tbody");
    thead = document.createElement("thead");

    table.append(thead);
    table.append(tbody);

    table = d3.select("#gen-table");
    booleans = cfgsrc["booleans"] ? cfgsrc["booleans"] : [];
    choices = cfgsrc["choices"] ? cfgsrc["choices"] : [];
    enums = cfgsrc["enums"] ? cfgsrc["enums"] : {};
    numbers = cfgsrc["numbers"] ? cfgsrc["numbers"] : {};

    
    names = booleans.concat(Object.keys(enums)).concat(Object.keys(numbers)).concat(choices.map((_,i)=>`Group ${i+1}`));
    console.log(names)

    table.select('thead')
        .selectAll('th')
        .data(names)
        .enter()
        .append("th")
        .text(d => d)
    
    // Create the selects manually is easier than using d3
    
    for (b of booleans) {
        let select = new CustomSelect("Any", null);
        select.name = b;

        select.add_option("True", true);
        select.add_option("False", false);

        //select.onchange = e => config_select_change(e);
        select.add_selection_listener((option) => config_select_change(select, option));
        cell = document.createElement('td');
        
        select.add_to_parent(cell);
        tbody.append(cell);

        bool_selects.push(select);
    }
    for(e in enums) {
        //select = document.createElement('select');
        let select = new CustomSelect("Any", null);
        select.name = e;
        
        for(value of enums[e]) {
            //select.append(createOption(value, value))
            select.add_option(value, value);
        }
        //select.onchange = event => config_select_change(event, e);
        select.add_selection_listener((option) => {
            config_select_change(select, option);
        });
        cell = document.createElement('td');
        select.add_to_parent(cell);
        tbody.append(cell);

        enum_selects.push(select);
    }

    for (let n in numbers) {

        if (numbers[n].length != 3) continue;

        let cell = document.createElement('td');
        let div = document.createElement('div');
        let checkbox = document.createElement('input');
        let slider = document.createElement('input');

        let label = document.createElement("label");

        div.append(checkbox);
        div.append(slider);
        div.append(label);
        cell.append(div);
        tbody.append(cell);

        div.classList.add('slider-input-container');

        checkbox.type = 'checkbox';

        slider.type = "range";
        slider.min = numbers[n][0];
        slider.max = numbers[n][1];
        x = ((numbers[n][0] + numbers[n][1]) / 2).toFixed(numbers[n][2]);
        slider.step = (0.1 ** numbers[n][2]).toFixed(numbers[n][2]);
        slider.value = x;
        slider.disabled = true;

        label.style["width"] = "48pt";

        slider.addEventListener('input', (e) => {
            let value = e.target.value;
            label.textContent = value;
            config_number_change(n, value);
        });

        checkbox.addEventListener('change', (e) => {
            if (e.target.checked) {
                slider.disabled = false;
                label.style["visibility"] = "visible";
                label.textContent = slider.value;
                config_number_change(n, slider.value);
            } else {
                slider.disabled = true;
                label.style["visibility"] = "hidden";
                config_number_change(n, null);
            }
        })

        number_divs[n] = div;
    }

    for (let i in choices) {
        let group = choices[i];
        let cell = document.createElement('td');
        let select = new CustomSelect("Any", null);
        select.name = i
        for (choice of group) {
            select.add_option(choice, choice);
        }
        select.add_selection_listener((option) => config_choice_change(select, option));
        select.add_to_parent(cell);
        tbody.append(cell);

        choice_selects.push(select);
    }
        
    
}

function config_select_change(select, option) {
    if (option.value == null) {
        delete CONFIG[select.name];
    } else {
        CONFIG[select.name] = option.value;
    }
    refresh_probas();
}

function config_choice_change(select, option) { 
    for (name of Array.from(select.options).map(o => o.value)) {
        if (name) delete CONFIG[name];
    }
    if (option.value) {
        CONFIG[option.value] = true;
    }
    refresh_probas();
}

function config_number_change(name, value) {
    value = parseFloat(value);
    if (isNaN(value)) {
        delete CONFIG[name];
    } else {
        let prev_val = CONFIG[name];
        CONFIG[name] = value;
        if (isNaN(prev_val)) {
            refresh_probas();
        } else {
            for (let limits of PROBAS["numbers"][name]["limits"]) {
                if (prev_val <= limits.upper && prev_val >= limits.lower &&
                    !(value <= limits.upper && value >= limits.lower)
                    ) {
                        refresh_probas();
                    }
            }
        }
    }
}

function createOption(text, value) {
    option = document.createElement("option");
    if (name) option.name = name;
    option.innerText = text;
    option.value = value;
    return option;
}

function update_selector() {
    for (select of enum_selects) {
        update_background_enum(select);
    }
    for (select of bool_selects) {
        update_background_bool(select);
    }
    for (group of choice_selects) {
        update_background_choice(group);
    }
}

function update_background_enum(select) {
    for (option of select.options) {

        let value = option.value;
        let proba;
        if (value == null)
            proba = PROBAS["enums"][select.name]["default"];
        else
            proba = PROBAS["enums"][select.name]["values"][value];
        option.color = gradient(proba * 100, RED, GREEN);
    }
    set_background(select.selection_div, select.selected_option.color);
    
}

function update_background_bool(select) {
    for (option of select.options) {

        let value = option.value;
        let proba;
        if (value == null)
            proba = PROBAS["booleans"][select.name]["default"];
        else
            proba = PROBAS["booleans"][select.name][value ? "true" : "false"];
        option.color = gradient(proba * 100, RED, GREEN);
    }
    set_background(select.selection_div, select.selected_option.color);
    
}

function update_background_choice(select) {
    for (option of select.options) {
        let value = option.value;
        let proba = PROBAS["choices"][option.name];
        option.color = gradient(proba * 100, RED, GREEN);
    }
    // TODO set background (need to compute the probability for any of them)
}

function refresh_probas() {
    console.log("Refersh");
    $.post("/predict", CONFIG, result => {
        PROBAS = JSON.parse(result);
        update_selector();
    });
}