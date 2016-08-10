
$(document).ready(function() {
    cuteform($('#id_evolve_to'), {
	'images': evolution_images,
    });
    // Add ownedpokemon edited to the ones to reload
    if (typeof ownedpokemons_to_reload != 'undefined') {
	var id = evolved_ownedpokemon;
	if (ownedpokemons_to_reload.indexOf(id) == -1) {
	    ownedpokemons_to_reload.push(id);
	}
    }
});
