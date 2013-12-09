var testData = testData(['Credits', 'Used'],
        2),// just 25 points, since there are lots of charts
    pieSelect = d3.select("#sources-chart-pie"),
    pieFooter = d3.select("#data-chart-footer"),
    lineChart;

function pieChartUpdate(d){
    d.disabled = !d.disabled;
    d3.select(this)
        .classed("disabled", d.disabled);
    if (!pieChart.pie.values()(testData).filter(function(d) { return !d.disabled }).length) {
        pieChart.pie.values()(testData).map(function(d) {
            d.disabled = false;
            return d;
        });
        pieFooter.selectAll('.control').classed('disabled', false);
    }
    d3.select("#sources-chart-pie svg").transition().call(pieChart);
}
 

nv.addGraph(function() {

    /*
     * we need to display total amount of visits for some period
     * calculating it
     * pie chart uses y-property by default, so setting sum there.
     */
    for (var i = 0; i < testData.length; i++){
        testData[i].y = Math.floor(d3.sum(testData[i].values, function(d){
            return d.y;
        }))
    }

    var chart = nv.models.pieChartTotal()
        .x(function(d) {return d.key })
        .margin({top: 0, right: 20, bottom: 20, left: 20})
        .values(function(d) {return d })
        .color(COLOR_VALUES)
        .showLabels(false)
        .showLegend(false)
        .tooltipContent(function(key, y, e, graph) {
            return '<h4>' + key + '</h4>' +
                '<p>' +  y + '</p>'
        })
        .total(function(count){
            return "<div class='visits'>" + count + "<br/> Credits left </div>"
        })
        .donut(true);
    chart.pie.margin({top: 10, bottom: -20});

    var sum = d3.sum(testData, function(d){
        return d.y;
    });
    pieFooter
        .append("div")
        .classed("controls", true)
        .selectAll("div")
        .data(testData)
        .enter().append("div")
        .classed("control", true)
        .style("border-top", function(d, i){
            return "3px solid " + COLOR_VALUES[i];
        })
        .html(function(d) {
            return "<div class='key'>" + d.key + "</div>"
                + "<div class='value'>145,000</div>";
        })
        .on('click', function(d) {
            pieChartUpdate.apply(this, [d]); 
        });

    d3.select("#sources-chart-pie svg")
        .datum([testData])
        .transition(500).call(chart);
    nv.utils.windowResize(chart.update);

    pieChart = chart;

    return chart;
});

