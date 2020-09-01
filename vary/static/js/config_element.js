class EnumOption {

    get name() {
        return this._name;
    }

    set name(n) {
        this._name = n;
        this.refreshNameLabel(n);
    }

    get div() {
        return this.mainDiv;
    }

    constructor(name) {
        
        this._name = name;

        // The div containing the element, a row using bootstrap classes for the layout
        this.mainDiv = document.createElement("div");
        this.mainDiv.classList.add("row", "w-100");

        // Left part with the label
        this.nameLabel = document.createElement('label');
        this.nameLabel.classList.add("col");

        // Right part with the options
        let right_col_div = document.createElement("div");
        right_col_div.classList.add("col-auto");

        this.selectionDiv = document.createElement('div');
        this.selectionDiv.classList.add("btn-group", "btn-group-sm", "btn-group-toggle");
        this.selectionDiv.setAttribute("role", "group");
        this.selectionDiv.setAttribute("data-toggle", "buttons");
        right_col_div.appendChild(this.selectionDiv);

        this.options = {};
        this.selectedOption = null;

        this.selectionChangeListeners = [];
        
        this.mainDiv.appendChild(this.nameLabel);
        this.mainDiv.appendChild(right_col_div);

        this.addOption("Any", null);
        this.selectOption(null);
        
        this.refreshNameLabel();
    }

    refreshNameLabel(name) {
        this.nameLabel.innerHTML = `${this.name} :`.bold();
    }

    addOption(name, value) {
        if(this.options[name] == null) {
            let label = document.createElement('label');
            label.textContent = name || "Any";
            label.classList.add("btn", "btn-secondary");

            let radio = document.createElement('input');
            radio.type = "radio";
            radio.name = this.name;

            label.appendChild(radio);

            let nb_options = this.selectionDiv.children.length;
            if (nb_options == 0) {
                label.classList.add("active");
                radio.checked = true;
                this.selectionDiv.appendChild(label);
            } else {
                this.selectionDiv.insertBefore(label, this.selectionDiv.children[nb_options-1]);
            }
            
            
            label.addEventListener('click', (event) => {
                this.selectOption(name);
            });

            this.options[name] = value;
        }

    }

    addSelectionChangeListener(listener) {
        this.selectionChangeListeners.push(listener);
    }

    callSelectionChangeListeners(newVal, oldVal) {
        for (let listener of this.selectionChangeListeners) {
            listener(newVal, oldVal);
        }
    }

    selectOption(name) {
        let value = this.options[name];
        if (this.selectedOption == value) {
            return;
        }
        let old = this.selectedOption;
        this.selectedOption = value;
        this.callSelectionChangeListeners(value, old);
    }

    setColor(name, color) {
        for (let c of this.selectionDiv.children) {
            if(c.textContent == name) {
                c.style["background-color"] = color;
            }
        }
    }

}

class BooleanOption extends EnumOption {
    constructor(name) {
        super(name);
        this.addOption("True", true);
        this.addOption("False", false);
    }
}

class GroupOption extends EnumOption {
    
    get name() {
        return null;
    }
    set name(n) {}
    constructor() {
        super("");
        this.mainDiv.removeChild(this.nameLabel);
        this.selectionDiv.parentNode.classList.add("mx-auto");
    }

    
}

class NumberOption {
    get div() {
        return this.mainDiv;
    }

    get name() {
        return this._name;
    }
    set name(n) {
        this._name = n;
        this.refreshNameLabel();
    }

    get min() {
        return this._min;
    }

    set min(m) {
        this._min = m;
        this.refreshRangeInput();
    }

    get max() {
        return this._max;
    }
    set max(m) {
        this.max = m;
        this.refreshRangeInput();
    }

    get step() {
        return this._step;
    }

    set step(s) {
        this._step;
        this.refreshRangeInput();
    }

    constructor(name, min, max, step) {
        this._min = min;
        this._max = max;
        this._step = step;
        this._name = name;


        let mainDiv = document.createElement('div');
        mainDiv.classList.add("row", "w-100");

        let selectionDiv = document.createElement('div');
        selectionDiv.classList.add("col-auto");
        
        let nameLabel = document.createElement("label");
        nameLabel.classList.add("col");

        let valueLabel = document.createElement("label");
        valueLabel.style["visibility"] = "hidden";

        let rangeInput = document.createElement("input");
        rangeInput.type = "range";
        rangeInput.disabled = true;
        rangeInput.classList.add("mx-2");
        
        rangeInput.addEventListener("input", (e) => {
            valueLabel.textContent = rangeInput.value;
        });
        
        rangeInput.addEventListener("change", () => this.updateValue());

        let disableCheckBox = document.createElement('input');
        disableCheckBox.type = "checkbox";
        disableCheckBox.addEventListener("change", () => {
            this.rangeInput.disabled = !disableCheckBox.checked;
            this.valueLabel.style["visibility"] = disableCheckBox.checked ? "visible" : "hidden";
            this.updateValue();
            this.callToggleListeners(disableCheckBox.checked);
        })

        this.mainDiv = mainDiv;
        this.nameLabel = nameLabel;
        this.rangeInput = rangeInput;
        this.valueLabel = valueLabel;
        this.disableCheckBox = disableCheckBox;
        this.changeListeners = [];
        this.toggleListeners = [];
        this.value = 0;


        this.mainDiv.appendChild(nameLabel);
        selectionDiv.appendChild(valueLabel);
        selectionDiv.appendChild(rangeInput);
        selectionDiv.appendChild(disableCheckBox);
        this.mainDiv.appendChild(selectionDiv);

        this.value = this.rangeInput.value;
        this.refreshRangeInput();
        this.refreshNameLabel();
    }

    updateValue() {
        let oldVal = this.value;
        this.value = this.rangeInput.value;
        this.callChangeListeners(this.value, oldVal);
    }

    addChangeListener(listener) {
        this.changeListeners.push(listener);
    }

    callChangeListeners(newVal, oldVal) {
        for (let listener of this.changeListeners) {
            listener(newVal, oldVal);
        }
    }

    addToggleListener(listener) {
        this.toggleListeners.push(listener);
    }

    callToggleListeners(enabled) {
        for (let listener of this.toggleListeners) {
            listener(enabled);
        }
    }

    refreshNameLabel() {
        this.nameLabel.innerHTML = `${this.name} :`.bold();
    }

    refreshRangeInput() {
        this.rangeInput.min = this.min;
        this.rangeInput.max = this.max;
        this.rangeInput.step = this.step;

        this.rangeInput.value = this.min;
        this.valueLabel.textContent = this.min;
    }
}
