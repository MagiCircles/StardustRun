
function onLevelChange() {
    var level = $('#id_level').val();
    if (level == "") {
	level = 0;
    } else {
	level = parseInt(level);
    }
    if (level < 5) {
	$('#id_team').closest('.form-group').hide();
    } else {
	$('#id_team').closest('.form-group').show();
    }
}

$(document).ready(function() {
    multiCuteForms({
	'starter_id': function(id, name) {
	    return starters_images[id];
	},
	'team': true,
    });
    onLevelChange();
    $('#id_level').change(onLevelChange);
});
