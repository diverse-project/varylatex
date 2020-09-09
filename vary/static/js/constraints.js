const CONFIG = {};
let PROBAS = {};
let has_data = false;
let filter_generation = false;

let nb_variables = 0;

const RED = "#ff2020";
const GREEN = "#20ff20";

const enum_selects = [];
const bool_selects = [];
const choice_selects = [];

$('document').ready(function(){
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
        label.innerText = "Invalid input : please enter a number of documents between 1 and 100";
        return;
    }
    // else


    label.innerText = (reset ? "Generating" : "Adding" ) + " " + amount + " documents";

    route = '/generate_pdfs/' + amount;
    if (reset) {
        document.getElementsByClassName("table-container")[0].style["visibility"] = "hidden";
        table.getElementsByTagName("thead")[0].innerHTML = "";
        table.getElementsByTagName("tbody")[0].innerHTML = "";
    }

    let data = filter_generation ? JSON.stringify(CONFIG) : "{}"

    $.ajax({
        type: "POST",
        contentType: "application/json",
        url: route,
        data: data,
        success: csv => fill_table(csv, reset),

    }).then(() => {
        label.innerHTML = "<a href='/tree_img' target='_blank'>See decision tree</a>";
        refresh_probas();
    })
}

function fill_table(csv, reset) {
    console.log("OUI")
    has_data = true;
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
}

function build_pdf(data) {
    delete data[""]
    let pdf_viewer = document.getElementById("pdf_viewer");
    pdf_viewer.data = "";
    $.ajax({
        url: "/build_pdf",
        dataType: "json",
        contentType: "application/json",
        type: "POST",
        data: JSON.stringify(data),
        success: result => {
            pdf_viewer.data = "/build_pdf";
        }
    })
}

function fetch_congig_src() {
    $.ajax({
        url: "/config_src",
        type: 'GET',
        dataType: 'json',
        cache: false,
        success: load_config_src
    });
}

function load_config_src(config) {
    let config_div = document.getElementById("configurator");
    
    let booleans = config["booleans"];
    if (booleans) load_booleans(booleans);
    
    let enums = config["enums"];
    if(enums) load_enums(enums);

    let choices = config["choices"];
    if (choices) load_choices(choices);

    let numbers = config["numbers"];
    if (numbers) load_numbers(numbers);
        
}

function load_booleans(booleans) {
    nb_variables += booleans.length;

    let bool_div = document.getElementById("boolDiv");
    for (let name of booleans) {
        let bool_option = new BooleanOption(name);

        bool_option.addSelectionChangeListener((newValue, oldValue) => select_enum_bool_callback(name, newValue, oldValue));
        bool_div.appendChild(bool_option.div);
        bool_selects.push(bool_option);
    }
}

function load_enums(enums) {
    nb_variables += Object.keys(enums).length;

    let enum_div = document.getElementById("enumDiv");
    for (let name in enums) {
        let enum_option = new EnumOption(name);
        
        enum_option.addSelectionChangeListener((newValue, oldValue) => select_enum_bool_callback(name, newValue, oldValue));
        
        for (let option of enums[name]) {
            enum_option.addOption(option, option);
        }
        enum_div.appendChild(enum_option.div);
        enum_selects.push(enum_option);
    }
}

function load_choices(choices) {
    nb_variables += choices.length;
    CHOICES = choices

    let choice_div = document.getElementById("choiceDiv");
    for (let group of choices) {
        let group_option = new GroupOption();

        group_option.addSelectionChangeListener(select_choice_callback);

        for (option of group) {
            group_option.addOption(option, option);
        }
        choice_div.appendChild(group_option.div);
        choice_selects.push(group_option);
    }
}

function load_numbers(numbers) {
    nb_variables += Object.keys(numbers).length;

    let number_div = document.getElementById("numberDiv");
    for(let name in numbers) {

        let number_option = new NumberOption(
            name,
            numbers[name][0],
            numbers[name][1],
            (0.1 ** numbers[name][2]).toFixed(numbers[name][2])
        );

        number_option.addChangeListener((newValue, oldValue) => select_number_callback(name, newValue, oldValue));
        number_option.addToggleListener((enabled) => toggle_number_callback(name, enabled));

        number_div.appendChild(number_option.div);
    }
}

function select_enum_bool_callback(name, newValue, oldValue) {
    if (newValue == null) {
        delete CONFIG[name];
    } else {
        CONFIG[name] = newValue;
    }
    refresh_probas();
}

function select_choice_callback(newValue, oldValue) {
    delete CONFIG[oldValue];
    if (newValue != null) {
        CONFIG[newValue] = true;
    }
    refresh_probas();
}

function select_number_callback(name, newValue, oldValue) {
    CONFIG[name] = newValue;
    refresh_probas();
}

function toggle_number_callback(name, enabled) {
    if (!enabled) {
        delete CONFIG[name];
        refresh_probas();
    }
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
    
    for (option in select.options) {

        let value = select.options[option];
        let proba;
        if (value == null)
            proba = PROBAS["enums"][select.name]["default"];
        else
            proba = PROBAS["enums"][select.name]["values"][value];
        
        select.setColor(option, gradient(proba * 100, RED, GREEN));
    }
    //set_background(select.selection_div, select.selected_option.color);
    
}

function update_background_bool(select) {
    for (option in select.options) {
        let value = select.options[option];
        let proba;
        if (value == null)
            proba = PROBAS["booleans"][select.name]["default"];
        else
            proba = PROBAS["booleans"][select.name][value ? "true" : "false"];
        select.setColor(option, gradient(proba * 100, RED, GREEN));
    }
    //set_background(select.selection_div, select.selected_option.color);
    
}

function update_background_choice(select) {
    for (option in select.options) {
        let value = select.options[option];
        let proba = PROBAS["choices"][option];
        select.setColor(option, gradient(proba * 100, RED, GREEN));
    }
    // TODO set background (need to compute the probability for any of them)
}

function refresh_probas() {
    if (!has_data) return;
    let max_pages = 4;
    let url = "/predict/" + max_pages;

    $.ajax({
        url: url,
        dataType: "json",
        contentType: "application/json",
        type: "POST",
        data: JSON.stringify(CONFIG),
        success: result => {
            PROBAS = result;
            update_selector();
        }
    })
}

function filter_pressed() {
    let filterBtn = document.getElementById('filterBtn');
    
    if (filter_generation) {
        filterBtn.classList.add("active");
        
    } else {
        filterBtn.classList.remove("active");
        
    }
    
    filter_generation = ! filter_generation;
    filterBtn.innerText = `Generate documents using these constraints : ${filter_generation? "enabled" : "disabled"}`;
}