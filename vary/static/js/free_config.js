let CONFIG = {}
let nb_variables = 0;
let CHOICES = [];
let autoGen = false;

$('document').ready(function(){
    fetch_config_src();
});

function fetch_config_src() {
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
    update_config();
}

function select_choice_callback(newValue, oldValue) {
    delete CONFIG[oldValue];
    if (newValue != null) {
        CONFIG[newValue] = true;
    }
    update_config();
}

function select_number_callback(name, newValue, oldValue) {
    CONFIG[name] = newValue;
    update_config();
}

function toggle_number_callback(name, enabled) {
    if (!enabled) {
        delete CONFIG[name];
        update_config();
    }
}

function update_config() {
    if (autoGen || Object.keys(CONFIG).length == nb_variables) {
        build_pdf();
    }
}

function autogen_pressed() {
    let autoGenBtn = document.getElementById('autoGenBtn');
    
    if (autoGen) {
        autoGenBtn.classList.add("active");
        
    } else {
        autoGenBtn.classList.remove("active");
        
    }
    
    autoGen = ! autoGen;
    autoGenBtn.innerText = `Auto generate missing options : ${autoGen? "enabled" : "disabled"}`;
}

function build_pdf() {
    let pdf_viewer = document.getElementById('pdf_viewer');
    $.post('/build_pdf', CONFIG).then(()=>{
        pdf_viewer.data = "/build_pdf"
    })
}