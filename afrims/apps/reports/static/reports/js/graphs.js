google.load('visualization', '1', {'packages':['corechart', 'annotatedtimeline']});
google.setOnLoadCallback(getChartData);

function drawUsageChart(response) {
    var data = new google.visualization.DataTable();
    data.addColumn('date', 'Date');
    data.addColumn('number', 'Appointments');
    data.addColumn('number', 'Broadcast Messages');
    data.addColumn('number', 'Callback Service');
    data.addColumn('number', 'Cold Chain');
    var rows =[]; 
    $.each(response.range, function(i, r) {
        var day = new Date(r[0]);
        var stats = r[1];
        rows.push([day, stats.appointments.total, stats.broadcasts.total, stats.broadcasts.callbacks, stats.broadcasts.coldchain]);
    });
    data.addRows(rows);
    var chart = new google.visualization.LineChart(document.getElementById('usage-chart'));
    var options = {
        title: 'System Usage by Activity, Last 8 Months'
    };
    chart.draw(data, options);
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

function drawUsageBreakdown(response) {
    var stats = response.to_date;
    var data = google.visualization.arrayToDataTable([
        ['Activity', 'Messages'],
        ['Appointments', stats.appointments.total],
        ['Broadcast Messages', stats.broadcasts.total],
        ['Callback Service',  stats.broadcasts.callbacks],
        ['Cold Chain', stats.broadcasts.coldchain]
    ]);
    var chart = new google.visualization.PieChart(document.getElementById('usage-breakdown'));
    var options = {
        title: 'System Usage by Activity, To Date'
    };
    chart.draw(data, options);
    // Fix positioning after render
    $('#usage-breakdown').css({'top': '-140px'});
    $('#usage-breakdown').parents('.module').css({'margin-bottom': '-140px'});
}

function getChartData() {
    // Fetch chart data and render on callback
    var now = new Date().getTime();
    // System usage for past 8 months    
    $.getJSON($('#usage-chart').data('url'), {timestamp: now}, drawUsageChart);
    // System usage to date
    $.getJSON($('#usage-breakdown').data('url'), {timestamp: now}, drawUsageBreakdown);
    // Appointment reminders for past 8 months
    $.getJSON($('#reminders-chart').data('url'), {timestamp: now}, drawRemindersChart);
}
