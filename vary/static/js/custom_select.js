class CustomOption {
    /* ---- Fields

    - this.div : HTML div element containing the representation of the option
    - this._name : Displayed name of the option (use this.name to update the div)
    - this.value : The value corresponding to the option
    - this._color : Background color of the div (use this.color to update it)
    - this.parent : The CustomSelect element containing this option.

    ------------ */

    // Accessors

    get name() {return this._name;}
    set name(new_name) {
        this._name = new_name;
        this.div.innerText = new_name;
    }

    get color() {return this._color; }
    set color(new_color) {
        this._color = new_color;
        set_background(this.div, new_color);
    }

    // If color is omitted, the option has the default background of the "custom-option" class in the stylesheet
    constructor(name, value, color) {
        this.div = document.createElement("div");
        this.value = value;
        this.parent = null;
        this.name = name;
        this.color = color;

        this.div.classList.add("custom-option");

        let that = this;

        this.div.addEventListener('click', function(event) {
            that.parent.select_option(that);
        });

    }

    // Sets the parent select of this option and appends the div to its option list.
    bind_to_select(select) {
        this.parent = select;
        select.option_div.appendChild(this.div);
    }

    show() {
        this.div.classList.remove("option-collapsed");
    }
    
    hide() {
        this.div.classList.add("option-collapsed");
    }

}

/**
 * Represents an object similar to the html <select>, made of divs, that can handle background color.
 * 
 */
class CustomSelect {
    constructor(name, value, color) {
        this.div = document.createElement("div");
        this.div.classList.add("custom-select");

        this.options = [];
        this.selection_listeners = [];

        this.selection_div = document.createElement("div");
        this.selection_div.classList.add("custom-selected-option");

        this.option_div = document.createElement("div");
        this.option_div.classList.add("custom-select-options")

        this.div.appendChild(this.selection_div);
        this.div.appendChild(this.option_div);

        this.expanded = false;

        if (name) {
            let default_option = this.add_option(name, value, color);
            this.select_option(default_option);
        }

        let that = this;
        // Expand / collapse on click listener
        window.addEventListener("click", function(event) {
            let clicked_on_selection = that.selection_div.contains(event.target);
            (!clicked_on_selection || that.expanded)? that.collapse() : that.expand();
        });

    }

    add_option(name, value, color) {
        let customOption = new CustomOption(name, value, color);
        customOption.bind_to_select(this);
        this.options.push(customOption);
        return customOption;
    }

    add_selection_listener(listener) {
        this.selection_listeners.push(listener);
    }

    remove_selection_listener(listener) {
        let index = this.selection_listeners.indexOf(listener);
        if (index > -1) {
            this.selection_listeners.splice(index, 1);
        } 
    }

    select_option(option) {
        let prev_option = this.selected_option; 
        if (this.selected_option == option) return;
        
        if (prev_option) prev_option.show();
        option.hide();

        this.selected_option = option;
        this.selection_div.innerText = this.selected_option.name;

        set_background(this.selection_div, this.selected_option.color);

        for (let listener of this.selection_listeners) {
            listener(option, prev_option);
        }
    }

    add_to_parent(parent) {
        parent.appendChild(this.div);
        this.collapse();
    }

    expand() {   
        /*     
        for (let option of this.options) {
            if (option == this.selected_option) continue;
            option.show();
        }*/
        this.option_div.style["visibility"] = "visible";
        this.expanded = true;
    }

    collapse() {
        /*
        for (let option of this.options) {
            option.hide();
        }*/
        this.option_div.style["visibility"] = "collapse";
        this.expanded = false;
    }

}

function set_background(element, color) {
    if (color) 
        element.style["backgroundColor"] = color;
    else
        element.style.removeProperty("background-color");
    
}