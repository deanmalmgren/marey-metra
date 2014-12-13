(function (){

    // this is the time format for the spreadsheet
    var foia_time_format = d3.time.format('%m/%d/%y %H:%M')

    d3.csv("data/morning_train.csv", function (d) {
        return {
            corridor: d['Corridor'],
            train_number: +d['Train Number'],
            station: d['Station'],
            arrival: foia_time_format.parse(d['Arrival Date/Time']),
            departure: foia_time_format.parse(d['Departure Date/Time']),
            dwell: +d['Dwell (sec)'],
            minutes_late: +d['Minutes Late']
        }
    }, function (data) {

        // aggregate the rows by date
        var nest = d3.nest()
            .key(function (d) {return Math.floor(d.arrival.getTime() / 1000 / 86400)})
            .sortKeys(d3.ascending)
            .entries(data);

        marey_diagram(nest);
    })

}());

function time_of_day(t) {
    return new Date(1970, 0, 1, t.getHours(), t.getMinutes());
}

function marey_diagram(nest) {
    var margin = {top: 20, right: 20, bottom: 30, left: 100},
    width = 960 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

    var stations = nest[0].values.map(function (d){return d.station});

    function stationLabel(i) {
        return stations[i];
    }

    var x = d3.time.scale()
        .range([0, width]);

    var y = d3.scale.linear()
        .range([0, height]);

    var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom");

    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left")
        .tickValues(d3.range(stations.length))
        .tickFormat(stationLabel);

    var data = nest[0].values;

    var line = d3.svg.line()
        .x(function(d) { return x(time_of_day(d.arrival)); })
        .y(function(d, index) { return y(index); });

    var svg = d3.select("#marey-diagram").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    x.domain(d3.extent(data, function(d) { return time_of_day(d.arrival)}));
    y.domain(d3.extent(data, function(d, index) { return index; }));

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis);

    svg.selectAll("path.line")
        .data(nest).enter()
        .append("path")
        .attr("class", "line")
        .attr("d", function (d) {return line(d.values)});
}
