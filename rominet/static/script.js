stop_motors = true;
block_set_motors = false;
mouse_dragging = false;
yaw = 0;
pollTime = 1000;
refreshToggled = true;

$(document).ready(function () {
    $.jqx.theme = "dark";
    $("#jqxTabs").jqxTabs({ width: '100%',
                            height: '100%',
                            position: 'top',
                            selectionTracker: 'false',
                            scrollable: 'false',
                            animationType: 'fade'});

    $("#resetOdometryButton").jqxButton({ width: 120, height: 40, template: "warning" });
    $("#resetOdometryButton").on('click', function(){
        resetOdometry();
    });

    $("#batteryGauge").jqxGauge({
             ranges: [{startValue: 0, endValue: 6.5, style: {fill: '#FC6A6A',stroke: '#FC6A6A'}, endWidth: 1,
                       startWidth: 1},
                      {startValue: 6.5, endValue: 7, style: {fill: '#FCF06A', stroke: '#FCF06A'}, endWidth: 1,
                       startWidth: 1 },
                      {startValue: 7, endValue: 10, style: {fill: '#0C9A9A', stroke: '#0C9A9A'}, endWidth: 1,
                       startWidth: 1}],
             ticksMajor: {interval: 1, size: '9%'},
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
             ticksMinor: {interval: 500,size: '5%'},
             ticksMajor: {interval: 1000, size: '9%'},
             value: 0,
             min: 0,
             max: 4000,
             height: 70,
             width: 70,
             animationDuration: 100,
             labels: { visible: false },
             caption: { value: '0', position: 'bottom', offset: [0, 0], visible: true },
     });

    $("#jqxRefreshButton").jqxToggleButton({ width: '200', toggled: true});
    $("#jqxRefreshButton").on('click', function () {
        refreshToggled = $("#jqxRefreshButton").jqxToggleButton('toggled');
        if (refreshToggled) {
            $("#jqxRefreshButton").value = 'Refresh On';
            poll()
        }
        else
            $("#jqxRefreshButton").value = 'Refresh Off';
    });

     poll()
});


function init() {
  $("#joystick").bind("touchstart",touchmove);
  $("#joystick").bind("touchmove",touchmove);
  $("#joystick").bind("touchend",touchend);
  $("#joystick").bind("mousedown",mousedown);
  $("#joystick").bind("mousemove",mousemove);
  $("#joystick").bind("mouseup",mouseup);
  $('#jqxWidget').bind("mouseup",function (event) {
      setMotors(0, 0);
  });
}

function poll() {
  $.ajax({url: "/rominet/api/status"}).done(update_status);
  if(refreshToggled) {
      setTimeout(poll, pollTime);
  }
}

function update_status(json) {
      if(json["connected"]) {
          $("#button0").html(json["buttons"][0] ? '1' : '0');
          $("#button1").html(json["buttons"][1] ? '1' : '0');
          $("#button2").html(json["buttons"][2] ? '1' : '0');
          $("#yaw").html(Number((json["yaw"]).toFixed(2)));

          volts = Number(json["battery"]) / 1000.;
          $("#batteryGauge").jqxGauge({
             caption: { value: volts, position: 'bottom', offset: [0, 0], visible: true },
          });

          $('#batteryGauge').val(volts);

          speed = Number(json["speed"])
          $("#speedGauge").jqxGauge({
             caption: { value: speed, position: 'bottom', offset: [0, 0], visible: true },
          });
          $("#speedGauge").val(Number(json["speed"]));

          $("#positionX").html(Number((json["position"][0]).toFixed(2)));
          $("#positionY").html(Number((json["position"][1]).toFixed(2)));

          $("#maxSpeedLeft").html(json["max_speed"][0]);
          $("#encoderLeft").html(json["encoders"][0]);
          $("#maxSpeedRight").html(json["max_speed"][1]);
          $("#encoderRight").html(json["encoders"][1]);

          d = new Date();
          $("#web_cam").attr("src", "/rominet/api/camera?" + d.getTime());


          var yawDeg = json["yaw"] * 180 / 3.14159;
          var from = yaw;
          var to = yawDeg;
          if (from - to > 300) {
              to = to + 360;
          } else if (to - from > 300) {
              to = to - 360;
          }

           yaw = yawDeg;
      } else {
    }
}

function touchmove(e) {
  e.preventDefault();
  touch = e.originalEvent.touches[0] || e.originalEvent.changedTouches[0];
  dragTo(touch.pageX, touch.pageY);
}

function mousedown(e) {
  e.preventDefault();
  mouse_dragging = true;
  dragTo(e.pageX, e.pageY);
}

function mouseup(e) {
  if(mouse_dragging) {
    e.preventDefault();
    mouse_dragging = false;
  }
  setMotors(0,0);
}

function mousemove(e) {
  if(mouse_dragging) {
    e.preventDefault();
    dragTo(e.pageX, e.pageY);
  }
}

function dragTo(x, y) {
  elm = $('#joystick').offset();
  x = x - elm.left;
  y = y - elm.top;
  w = $('#joystick').width()
  h = $('#joystick').height()

  x = (x-w/2.0)/(w/2.0);
  y = (y-h/2.0)/(h/2.0);

  if(x < -1) x = -1;
  if(x > 1) x = 1;
  if(y < -1) y = -1;
  if(y > 1) y = 1;

  max = 100;
  left_motor = Math.round(max*(-y+x));
  right_motor = Math.round(max*(-y-x));

  if(left_motor > max) left_motor = max;
  if(left_motor < -max) left_motor = -max;

  if(right_motor > max) right_motor = max;
  if(right_motor < -max) right_motor = -max;

  setMotors(left_motor, right_motor);
}

function touchend(e) {
  e.preventDefault();
  setMotors(0, 0);
}

function setMotors(left, right) {
    if (left == 0 && right == 0) {
      stop_motors = true;
    }

  if(block_set_motors) return;
  block_set_motors = true;
  stop_motors = false;
  $("#joystick").html("Motors: " + left + " "+ right);
  var data = {
      left: left,
      right: right,
  };
  var request = $.ajax({url: "/rominet/api/motors",
          type: 'PUT',
          data: JSON.stringify(data),
          dataType: 'json',
          contentType: 'application/json; charset=utf-8'
    })
    request.always(setMotorsDone);
}

function setMotorsDone() {
  block_set_motors = false;
  if (stop_motors) {
    setMotors(0, 0);
  }
}

function setLeds() {
  red = $('#led_red')[0].checked ? 1 : 0;
  yellow = $('#led_yellow')[0].checked ? 1 : 0;
  green = $('#led_green')[0].checked ? 1 : 0;
  var data = {
      red: red,
      yellow: yellow,
      green: green,
  };

  $.ajax({url: "rominet/api/leds",
          type: 'PUT',
          data: JSON.stringify(data),
          dataType: 'json',
          contentType: 'application/json; charset=utf-8'
  });
}

function resetOdometry() {
  $.ajax({url: "rominet/api/reset_odometry",
          type: 'GET',
  });
}

function playNotes() {
  notes = $('#notes').val();
  var data = {
      notes: notes
  };
  $.ajax({url: "rominet/api/notes",
          type: 'PUT',
          data: JSON.stringify(data),
          dataType: 'json',
          contentType: 'application/json; charset=utf-8'
    });
}

function shutdown() {
  if (confirm("Really shut down the Raspberry Pi?"))
      $.ajax({url: "/rominet/api/shutdown",
              type: 'GET',
      });
}
