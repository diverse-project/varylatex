function gradient(perc, start_color, end_color) {
    let [r1,g1,b1] = start_color.slice(-6).match(/(..)/g).map(x => parseInt(x, 16));
    let [r2,g2,b2] = end_color.slice(-6).match(/(..)/g).map(x => parseInt(x, 16));

    color =
        Math.round(r1 + (r2-r1) * perc / 100) * 256 * 256 +
        Math.round(g1 + (g2-g1) * perc / 100) * 256  +
        Math.round(b1 + (b2-b1) * perc / 100);

    return '#' + ('000000' + color.toString(16)).slice(-6);
}