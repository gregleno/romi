"use strict";

var fastPollTime = 200;
var pollTime = slowPollTime;
var slowPollTime = 1000;

var cameraPollTime = 1000;
var refreshTabVisible = true

$(document).ready(function () {
    $.jqx.theme = "dark";
    $("#jqxTabs").jqxTabs({
        width: '100%',
        height: '100%',
        position: 'top',
        selectionTracker: 'false',
        scrollable: 'false',
        animationType: 'fade'
    });

    $('#jqxTabs').on('selected', function (event) {
        var selectedTab = event.args.item;
        refreshTabVisible = selectedTab == 0;
        if (refreshTabVisible) {
            poll();
            pollCamera();
        }
    });

    $("#resetOdometryButton").jqxButton();
    $("#resetOdometryButton").on('click', function () {
        resetOdometry();
    });

    $("#batteryGauge").jqxGauge({
        ranges: [{
            startValue: 0, endValue: 6.5, style: { fill: '#FC6A6A', stroke: '#FC6A6A' }, endWidth: 1,
            startWidth: 1
        },
        {
            startValue: 6.5, endValue: 7, style: { fill: '#FCF06A', stroke: '#FCF06A' }, endWidth: 1,
            startWidth: 1
        },
        {
            startValue: 7, endValue: 10, style: { fill: '#0C9A9A', stroke: '#0C9A9A' }, endWidth: 1,
            startWidth: 1
        }],
        ticksMajor: { interval: 1, size: '9%' },
        value: 0,
        min: 0,
        max: 10,
        height: 70,
        width: 70,
        animationDuration: 1,
        caption: { value: '0', position: 'bottom', offset: [0, 0], visible: true },
        labels: { visible: false }
    });
    $("#speedGauge").jqxGauge({
        ticksMinor: { interval: 500, size: '5%' },
        ticksMajor: { interval: 1000, size: '9%' },
        value: 0,
        min: 0,
        max: 4000,
        height: 70,
        width: 70,
        animationDuration: 200,
        labels: { visible: false },
        caption: { value: '0', position: 'bottom', offset: [0, 0], visible: true },
    });

    $("#jqxRefreshButton").jqxToggleButton({ toggled: true });
    $("#jqxRefreshButton").on('click', function () {
        toggleRefreshLabel();
        poll();
        pollCamera();
    });

    poll();
    pollCamera();
    setMotors(0, 0);
    programmer_init();
    joystick_init();
    keypad_init();
    $("#led_red").jqxToggleButton({ width: '50', toggled: true, template: 'danger' });
    $("#led_green").jqxToggleButton({ width: '50', toggled: true, template: 'success' });
    $("#led_yellow").jqxToggleButton({ width: '50', toggled: true, template: 'warning' });
    $('#led_red').on('click', setLeds);
    $('#led_green').on('click', setLeds);
    $('#led_yellow').on('click', setLeds);


});

function toggleRefreshLabel() {
    var refreshToggled = $("#jqxRefreshButton").jqxToggleButton('toggled');
    if (refreshToggled) {
        $("#jqxRefreshButton").val('Refresh On');
    }
    else
        $("#jqxRefreshButton").val('Refresh Off');
}

function pollCamera() {
    if ($("#jqxRefreshButton").jqxToggleButton('toggled') && refreshTabVisible) {
        var d = new Date();
        $("#web_cam").attr("src", "/rominet/api/camera?" + d.getTime());
        setTimeout(pollCamera, cameraPollTime)
    }
}

function poll() {
    if ($("#jqxRefreshButton").jqxToggleButton('toggled') && refreshTabVisible) {
        $.ajax({ url: "/rominet/api/status" }).done(update_status);
    }
}

var previousX = 123;
var previousY = 134;
function update_status(json) {
    if (json["connected"]) {
        $("#button0").html(json["buttons"][0] ? '1' : '0');
        $("#button1").html(json["buttons"][1] ? '1' : '0');
        $("#button2").html(json["buttons"][2] ? '1' : '0');
        $("#yaw").html(Number((json["yaw"]).toFixed(2)));

        var volts = Number((Number(json["battery"]) / 1000.)).toFixed(1);
        $("#batteryGauge").jqxGauge({
            caption: { value: volts, position: 'bottom', offset: [0, 0], visible: true },
        });

        $('#batteryGauge').val(volts);

        var speed = Number(json["speed"])
        $("#speedGauge").jqxGauge({
            caption: { value: speed, position: 'bottom', offset: [0, 0], visible: true },
        });
        $("#speedGauge").val(Number(json["speed"]));

        var x = Number((json["position"][0]).toFixed(3));
        var y = Number((json["position"][1]).toFixed(3));

        if (previousX == x && previousY == y)
            pollTime = slowPollTime;
        else
            pollTime = fastPollTime;
        previousX = x;
        previousY = y;

        $("#positionX").html(x);
        $("#positionY").html(y);

        $("#encoderLeft").html(json["encoders"][0]);
        $("#encoderRight").html(json["encoders"][1]);
        setTimeout(poll, pollTime);
    } else {
        if ($("#jqxRefreshButton").jqxToggleButton('toggled')) {
            $('#jqxRefreshButton').jqxToggleButton('toggle');
            toggleRefreshLabel();
        }
    }
}


function setLeds() {
    var red = $("#led_red").jqxToggleButton('toggled') ? 0 : 1;
    var yellow = $("#led_yellow").jqxToggleButton('toggled') ? 0 : 1;
    var green = $("#led_green").jqxToggleButton('toggled') ? 0 : 1;

    var data = {
        red: red,
        yellow: yellow,
        green: green,
    };

    $.ajax({
        url: "rominet/api/leds",
        type: 'PUT',
        data: JSON.stringify(data),
        dataType: 'json',
        contentType: 'application/json; charset=utf-8'
    });
}

function resetOdometry() {
    $.ajax({
        url: "rominet/api/reset_odometry",
        type: 'GET',
    });
}

function playNotes() {
    var notes = $('#notes').val();
    var data = {
        notes: notes
    };
    $.ajax({
        url: "rominet/api/notes",
        type: 'PUT',
        data: JSON.stringify(data),
        dataType: 'json',
        contentType: 'application/json; charset=utf-8'
    });
}

function shutdown() {
    if (confirm("Really shut down the Raspberry Pi?"))
        $.ajax({
            url: "/rominet/api/shutdown",
            type: 'GET',
        });
}
