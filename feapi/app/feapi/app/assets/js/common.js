function getCurrentPageJsonUrl() {
    const formatRegex = /(\?|&)format=html\b/;
    const jsonFormat = "format=json"
    if (window.location.href.match(formatRegex)) {
        return window.location.href.replace(formatRegex, "$1" + jsonFormat)
    }
    const builder = [window.location.href];
    if (window.location.search.length) {
        builder.push("&");
    } else {
        builder.push("?");
    }
    builder.push(jsonFormat)
    return builder.join("");
}

function mapFeatures(dataHandler) {
    const map = L.map("map");
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
    fetch(getCurrentPageJsonUrl())
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            dataHandler(data, map);
        });
}
