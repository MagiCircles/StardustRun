
$(document).ready(function() {
    multiCuteForms({
	'starter_id': function(id, name) {
	    return starters_images[id];
	},
	'team': true,
    });
});
