(function (){

    // cast the punchcard data into the proper format
    var datetime_format = d3.time.format(global_data.DATETIME_FORMAT);
    global_data.punchcards.forEach(function (d) {
        d.scheduled_time = datetime_format.parse(d.scheduled_time);
        d.tracked_time = datetime_format.parse(d.tracked_time);
    });

    // create the diagram
    marey_diagram(global_data.punchcards, global_data.distances);

    // // this is the time format for the spreadsheet
    // var foia_time_format = d3.time.format('%m/%d/%y %H:%M');
    // var schedule_time_format = d3.time.format(' %H:%M:%S');
    // var data;
    // d3.csv("data/morning_train.csv", function (d) {
    //     var t0 = foia_time_format.parse(d['Arrival Date/Time']);
    //     var t1 = foia_time_format.parse(d['Departure Date/Time']);
    //     return {
    //         // corridor: d['Corridor'],
    //         // train_number: +d['Train Number'],
    //         station: d['Station'],
    //         arrival: t0,
    //         t: time_of_day(t1),
    //         departure: t1,
    //         // dwell: +d['Dwell (sec)'],
    //         minutes_late: +d['Minutes Late']
    //     }
    // }, function (_data) {
    //     data = _data;
    //     d3.csv("data/morning_schedule.csv", function (d) {
    //         return {
    //             t: time_of_day(schedule_time_format.parse(d[' arrival_time'])),
    //             station: d[' stop_id']
    //         }
    //     }, function (schedule) {
    //         marey_diagram(data, schedule);
    //     })
    // })

}());

function marey_diagram(punchcards, distances) {

    // aggregate the rows by date
    var nest = d3.nest()
        .key(function (d) {return Math.floor(d.tracked_time.getTime() / 1000 / 86400)})
        .sortKeys(d3.ascending)
        .entries(punchcards);

    // TODO: There is  probably a more robust way to do this in the situation
    // where the first element of the next does not actually have all the values
    var stations = nest[0].values.map(function (d){return d.stop_id});
    function stationLabel(distance, i) {
        return stations[i];
    }

    var margin = {top: 20, right: 20, bottom: 30, left: 100},
    width = 960 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

    function time_of_day(t) {
        return new Date(1970, 0, 1, t.getHours(), t.getMinutes());
    }
    var x = d3.time.scale()
        .range([0, width])
        .domain(d3.extent(punchcards, function(d) {
            return time_of_day(d.tracked_time);
        }));

    var y = d3.scale.linear()
        .range([0, height])
        .domain(d3.extent(distances));

    var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom");

    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left")
        .tickValues(distances)
        .tickFormat(stationLabel);

    var tracked_line = d3.svg.line()
        .x(function(d) { return x(time_of_day(d.tracked_time)); })
        .y(function(d, i) { return y(distances[i]); });
    var scheduled_line = d3.svg.line()
        .x(function(d) { return x(time_of_day(d.scheduled_time)); })
        .y(function(d, i) { return y(distances[i]); });

    var svg = d3.select("#marey-diagram").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var band_height = 4;
    svg.append("g")
        .attr("class", "y bands")
        .selectAll("rect")
        .data(stations).enter()
        .append("rect")
        .attr("x", 0)
        .attr("width", width)
        .attr("y", function(station, i){ return y(distances[i])-band_height/2})
        .attr("height", band_height)

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis);

    svg.selectAll("path.scheduled.line")
        .data(nest).enter()
        .append("path")
        .attr("class", "scheduled line")
        .attr("d", function (d) {return scheduled_line(d.values)});

    svg.selectAll("path.tracked.line")
        .data(nest).enter()
        .append("path")
        .attr("class", "tracked line")
        .attr("d", function (d) {return tracked_line(d.values)});

}
