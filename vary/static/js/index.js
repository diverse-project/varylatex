function closeTabs(tabId) {
    let tabs = document.getElementsByClassName("tab-content");
    for (tab of tabs) {
        tab.style["display"] = "none";
    }
}

function toggleButtonsOff() {
    let buttons = document.getElementsByClassName("tab-button");
    for (button of buttons) {
        button.classList.remove("active")
    }
}

function openTab(event, tabId) {
    closeTabs();
    document.getElementById(tabId).style["display"] = "flex";
    event.currentTarget.classList.add("active");
}