function joystick_init() {
  $("#joystick").bind("touchstart", touchmove);
  $("#joystick").bind("touchmove", touchmove);
  $("#joystick").bind("touchend", touchend);
  $("#joystick").bind("mousedown", mousedown);
  $("#joystick").bind("mousemove", mousemove);
  $("#joystick").bind("mouseup", mouseup);
  $('#jqxWidget').bind("mouseup", function (event) {
      setMotors(0, 0);
  });
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