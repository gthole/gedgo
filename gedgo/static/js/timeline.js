/* global d3 */
'use strict';

const gid = d3.select("#timeline").attr("data-gid"),
      pid = d3.select("#timeline").attr("data-pid");

d3.json("/gedgo/" + gid + "/timeline/" + pid + "/", (data) => {
    const events = data.events;
    if (events.length < 1) {
        $("#timeline-pod").remove();
        return;
    }
    const birthyear = data.start,
          deathyear = data.end,
          hscale = d3.scale.linear()
                      .domain([0, 35])
                      .range([20, 400]);

    //Width and height
    const w = 480,
          h = hscale(deathyear - birthyear),
          scale = d3.scale.linear()
                    .domain([birthyear, deathyear])
                    .range([10, h - 10]);

    // Create SVG element
    const svg = d3.select("#timeline")
       .append("svg:svg")
       .attr("width", w)
       .attr("height", h);

    svg.selectAll("line")
        .data([1])
        .enter()
        .append("line")
        .attr("x1", w/2).attr("y1", 10)
        .attr("x2", w/2).attr("y2", h - 10)
        .attr("stroke", "teal");

    svg.selectAll("circle")
        .data(events)
        .enter()
        .append("circle")
        .attr("cx", w/2)
        .attr("cy", (d) => scale(d.year))
        .attr("r", 5)
        .attr("fill", d => (d.year === birthyear || d.year === deathyear) ? "teal" : "white")
        .attr("stroke-width", 3)
        .attr("stroke", d => (d.type === 'personal') ? "teal" : "orange");

    svg.selectAll("text")
          .data(events)
          .enter()
          .append("text")
        .text((d) => d.year + ': ' + d.text)
          .attr("x", d => (d.type === 'personal') ? w/2 + 20 : w/2 - 20)
          .attr("y", (d) => scale(d.year) + 5)
          .attr("text-anchor", d => (d.type === 'personal') ? "start" : "end")
          .attr("font-family", "Baskerville")
          .attr("font-size", "9pt")
          .attr("fill", "gray");
});
