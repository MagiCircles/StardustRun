
$(document).ready(function() {
    // Add ownedpokemon edited to the ones to reload
    if (typeof ownedpokemons_to_reload != 'undefined') {
	var id = parseInt($('#id_thing_to_delete').val());
	if (ownedpokemons_to_reload.indexOf(id) == -1) {
	    ownedpokemons_to_reload.push(id);
	}
    }
});
