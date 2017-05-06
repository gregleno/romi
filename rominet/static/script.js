// Copyright Pololu Corporation.  For more information, see https://www.pololu.com/
stop_motors = true
block_set_motors = false
mouse_dragging = false

function init() {
  poll()
  $("#joystick").bind("touchstart",touchmove)
  $("#joystick").bind("touchmove",touchmove)
  $("#joystick").bind("touchend",touchend)
  $("#joystick").bind("mousedown",mousedown)
  $(document).bind("mousemove",mousemove)
  $(document).bind("mouseup",mouseup)
}

function poll() {
  $.ajax({url: "/rominet/api/status"}).done(update_status)
  if(stop_motors && !block_set_motors)
  {
    setMotors(0,0);
    stop_motors = false
  }
}

function update_status(json) {
    try {
      if(json["connected"]) {
          $("#button0").html(json["buttons"][0] ? '1' : '0')
          $("#button1").html(json["buttons"][1] ? '1' : '0')
          $("#button2").html(json["buttons"][2] ? '1' : '0')
          $("#battery").html(json["battery"])
          $("#yaw").html(json["yaw"])
          $("#position").html(json["position"])
          $("#speed").html(json["speed"])
          $("#maxSpeedLeft").html(json["max_speed_left"])
          $("#maxSpeedRight").html(json["max_speed_right"])
          $("#encoders0").html(json["encoders"][0])
          $("#encoders1").html(json["encoders"][1])
      } else {
      }
  } catch(err) {

  }

    setTimeout(poll, 100)
}

function touchmove(e) {
  e.preventDefault()
  touch = e.originalEvent.touches[0] || e.originalEvent.changedTouches[0];
  dragTo(touch.pageX, touch.pageY)
}

function mousedown(e) {
  e.preventDefault()
  mouse_dragging = true
  dragTo(e.pageX, e.pageY)
}

function mouseup(e) {
  if(mouse_dragging)
  {
    e.preventDefault()
    mouse_dragging = false
    stop_motors = true
  }
}

function mousemove(e) {
  if(mouse_dragging)
  {
    e.preventDefault()
    dragTo(e.pageX, e.pageY)
  }
}

function dragTo(x, y) {
  elm = $('#joystick').offset();
  x = x - elm.left;
  y = y - elm.top;
  w = $('#joystick').width()
  h = $('#joystick').height()

  x = (x-w/2.0)/(w/2.0)
  y = (y-h/2.0)/(h/2.0)

  if(x < -1) x = -1
  if(x > 1) x = 1
  if(y < -1) y = -1
  if(y > 1) y = 1

  max = 100
  left_motor = Math.round(max*(-y+x))
  right_motor = Math.round(max*(-y-x))

  if(left_motor > max) left_motor = max
  if(left_motor < -max) left_motor = -max

  if(right_motor > max) right_motor = max
  if(right_motor < -max) right_motor = -max

  stop_motors = false
  setMotors(left_motor, right_motor)
}

function touchend(e) {
  e.preventDefault()
  stop_motors = true
}

function setMotors(left, right) {
  $("#joystick").html("Motors: " + left + " "+ right)

  if(block_set_motors) return
  block_set_motors = true
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
  block_set_motors = false
}

function setLeds() {
  red = $('#led_red')[0].checked ? 1 : 0
  yellow = $('#led_yellow')[0].checked ? 1 : 0
  green = $('#led_green')[0].checked ? 1 : 0
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
  })
}

function resetOdometry() {
  $.ajax({url: "rominet/api/reset_odometry",
          type: 'GET',
  })
}

function playNotes() {
  notes = $('#notes').val()
  var data = {
      notes: notes,
  };
  $.ajax({url: "rominet/api/notes",
          type: 'PUT',
          data: JSON.stringify(data),
          dataType: 'json',
          contentType: 'application/json; charset=utf-8'
})
}

function shutdown() {
  if (confirm("Really shut down the Raspberry Pi?"))
    return true
  return false
}
