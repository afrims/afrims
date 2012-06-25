google.load('visualization', '1', {'packages':['corechart', 'annotatedtimeline']});
google.setOnLoadCallback(getChartData);

function drawChart(response, title, element) {
    var data = new google.visualization.DataTable();
    data.addColumn('date', 'Date');
    data.addColumn('number', 'Incoming Messages');
    data.addColumn('number', 'Outgoing Messages');
    var rows =[];
    $.each(response, function(i, r) {
        rows.push([new Date(r[0]), r[1], r[2]]);
    });
    data.addRows(rows);
    var chart = new google.visualization.LineChart(document.getElementById(element));
    chart.draw(data, {displayAnnotations: false, title: title});
}

function drawRemindersChart(response) {
    var data = new google.visualization.DataTable();
    data.addColumn('date', 'Date');
    data.addColumn('number', '% of Appointments Confirmed');
    data.addColumn('number', '% of Reminders Confirmed');
    var rows =[];
    $.each(response.range, function(i, r) {
        var day = new Date(r[0]);
        var stats = r[1];
        rows.push([day, stats.appointments.percent, stats.reminders.percent]);
    });
    data.addRows(rows);
    var chart = new google.visualization.LineChart(document.getElementById('reminders-chart'));
    var options = {
        title: 'Appointment Reminders, Last 8 Months',
        vAxis: {maxValue: 100.0, minValue: 0.0},
        legend: {position: 'bottom'}
    };
    chart.draw(data, options);
}

function getChartData() {
    // Fetch chart data and render on callback
    // System usage for past 8 months
    var url = $('#usage-chart').data('url');
    var now = new Date().getTime();
    $.getJSON(url, {timestamp: now}, function(data) {drawChart(data, 'System Usage by Activity, Last 8 Months', 'usage-chart')});
    // System usage to date
    var data = google.visualization.arrayToDataTable([
        ['Activity', 'Messages'],
        ['Appointements',     11],
        ['Broadcast Messages',      2],
        ['Callback Service',  2],
        ['Cold Chain', 2],
    ]);
    var options = {
        title: 'System Usage by Activity, To Date'
    };
    var chart = new google.visualization.PieChart(document.getElementById('usage-breakdown'));
    chart.draw(data, options);
    // Appointment reminders for past 8 months
    var url = $('#reminders-chart').data('url');
    var now = new Date().getTime();
    $.getJSON(url, {timestamp: now}, drawRemindersChart);
}
