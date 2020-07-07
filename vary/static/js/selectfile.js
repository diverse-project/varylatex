let selection = '';
let selected = false;

$('document').ready(function(){
    $.get('/filenames', function(res) {
        let names = JSON.parse(res);
        let select = $("#file_select");
        console.log(names);

        for(filename of names) {
            let opt = document.createElement('option');
            opt.value = filename;
            opt.text = filename;
            select.append(opt);
        }
    })
});

function selection_changed() {
    let select = document.getElementById("file_select");
    let option = select.options[select.selectedIndex];
    selected = true;
    selection = option.value;
}