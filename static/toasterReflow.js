

function setHeater(state) {
  $.post('/control/heater', {state: state});
}
function setFan(state) {
  $.post('/control/fan', {state: state});
}

function populateProfileSelector() {
  if ($('#profile-display').length > 0) {
    $.getJSON('/profiles', function(profiles) {
      $.each(profiles, function(i, profile) {
        $('#profile-selector').append('<option value="'+profile+'">'+profile+'</option>');
      });
      // Force draw display with default selected profile:
      window.selected_profile = $('#profile-selector').val();
      drawProfileDisplay();
    });
    // Setup redraw on profile change:
    $('#profile-selector').change(function () {
      window.selected_profile = $('#profile-selector').val();
      drawProfileDisplay();
    });
  }
}

function drawProfileDisplay() {
  /* One-time draw of window.profile. */
  if ($('#profile-display').length == 0) return;
  $.getJSON('/profiles/'+window.selected_profile, function(profile) {
    var data = [];
    window.phase_marks = [];
    var time = 0;
    time_step_s = window.time_step/1000.0
    $.each(window.phases, function (i, phase) { 
      $.each(profile[phase], function (i, temp) {
        data.push([time*time_step_s,temp]);
        time += 1;
      });
      window.phase_marks.push({color: '#000', lineWidth: 1, 
                               xaxis: {from: time*time_step_s-time_step_s/2, 
                                       to: time*time_step_s-time_step_s/2}});
    });
    // Store the profile data series so we don't have to recalcuate for each
    // real-time update when running:
    window.profile_map = data;
    window.plot = $.plot('#profile-display', [{data: data, color: '#3333dd'}], 
                                {series: {lines: {show: true}},
                                 grid: {markings: phase_marks, 
                                        hoverable: true,
                                        mouseActiveRadius: 15},
                                 yaxis: {min: 0, max: 300, tickSize: 20},
                                 xaxis: {tickSize: 20}});
  });
}

function drawRealtimeDisplay() {
  $.getJSON('/realtime-data', function(realtime_data) {
      window.plot.setData([{data: window.profile_map, color: '#3333dd'},
                                {data: realtime_data, color: '#ee3333'}]);
      window.plot.draw();
  });
}

function enableReflowControls() {
  /* Enables all reflow controls. */
  $('#profile-selector').removeAttr('disabled');
  $('#start-reflow').removeAttr('disabled');
  $('#clear-plot').removeAttr('disabled');
  $('#heater-on').removeAttr('disabled');
  $('#heater-off').removeAttr('disabled');
  $('#fan-on').removeAttr('disabled');
  $('#fan-off').removeAttr('disabled');
}

function disableReflowControls() {
  /* Disables all controls that should not be enabled when reflowing. */
  $('#profile-selector').attr('disabled', 'disabled');
  $('#start-reflow').attr('disabled', 'disabled');
  $('#clear-plot').attr('disabled', 'disabled');
  $('#heater-on').attr('disabled', 'disabled');
  $('#heater-off').attr('disabled', 'disabled');
  $('#fan-on').attr('disabled', 'disabled');
  $('#fan-off').attr('disabled', 'disabled');
}

function startReflow() {
  $.post('/control/start',function (response) {
    disableReflowControls();
    window.oven_running = true;
  }); 
}

function stopReflow() {
  $.post('/control/stop', function(response) {
    enableReflowControls();
    window.oven_running = false;
  }); 
}


function updatePage() {
  if ($('#heater-state').length > 0) {
    $.getJSON('/control/heater', function(state) {
      $('#heater-state').html(state);
      if (state == 'on') {
        $('#heater-state').css("color", "#dd3333");
      } else {
        $('#heater-state').css("color", "#3333dd");
      }
    });
  }
  if ($('#fan-state').length > 0) {
    $.getJSON('/control/fan', function(state) {
      $('#fan-state').html(state);
    });
  }
  if ($('#temperature').length > 0) {
    $.getJSON('/control/temperature', function(temp) {
	$('#temperature').html(temp.toFixed(2)+"&deg;C");
    });
  }

  if ($('#reflow-phase').length > 0) {
    $.getJSON('/current-phase', function(phase) {
      if (!phase) {
        phase = 'Not running';
        $('#reflow-phase').css("color", "#dd3333");
      } else {
        phase = {'pre_soak' : 'Pre-soak',
                     'soak' : 'Soak',
                  'ramp_up' : 'Ramp up',
                     'peak' : 'Peak',
		     'cool' : 'Cool'}[phase];
        $('#reflow-phase').css("color", "#000000");
      }
      $('#reflow-phase').html(phase);
    });
  }

  if (window.oven_running == true) {
    drawRealtimeDisplay();
    $.getJSON('/status', function(status) {
      if (status == 'off') {
        stopReflow();
        //$.getJSON('/error', function(error) { 
        //  alert("Reflow aborted!:"+error); 
        //});
      }
    });
  }
}

$(document).ready(function() {
  // Grab a couple values and set as globals for using in calculations:
  $.getJSON('/phases', function(phases) {
    window.phases = phases;
  });
  $.getJSON('/time-step', function(time_step) {
    window.time_step = time_step;
  });
  
  $.getJSON('/status', function(status) {
    if (status == 'on') {
      window.oven_running = true;
      disableReflowControls();
    }
    else window.oven_running = false;
  });
  
  window.oven_temperature = [];
 
  populateProfileSelector();
  drawProfileDisplay();
  updatePage();
  setInterval(function() { updatePage(); }, 500);
});