
function updatePokemons() {
    $('[data-toggle="popover"]').popover();
    ajaxModals();
    handleAccountSelectChange();
    $('a[href="#addPokemon"]').unbind('click');
    $('a[href="#addPokemon"]').click(function(e) {
	e.preventDefault();
	var pokemon_link = $(this);
	var loader = pokemon_link.find('.flaticon-loading');
	var icon = pokemon_link.find('.add-button .flaticon-add');
	if (!loader.hasClass('is-loading')) {
	    icon.hide();
	    loader.show();
	    loader.addClass('is-loading');
	    var form = pokemon_link.closest('.pokemon').find('form');
	    form.ajaxSubmit({
		success: function(data) {
		    loader.removeClass('is-loading');
		    loader.hide();
		    pokemon_link.addClass('pokemon-seen');
		    icon.removeClass('flaticon-add');
		    icon.addClass('flaticon-checked');
		    icon.show();
		    pokemon_link.popover('destroy');
		    pokemon_link.unbind('click');
		    pokemon_link.prop('href', pokemon_link.data('item-url'));
		    pokemon_link.attr('data-ajax-url', pokemon_link.data('item-ajax-url'));
		    pokemon_link.attr('data-ajax-title', pokemon_link.data('item-ajax-title'));
		    form.hide();
		    ajaxModals();
		},
		error: genericAjaxError,
	    });
	}
	return false;
    });
}

function handleAccountSelectChange() {
    $('.pokemon-add-form select').unbind('change');
    $('.pokemon-add-form select').change(function() {
	$('.pokemon-add-form select').val($(this).val());
    });
}

$(document).ready(function() {
    cuteform($('#id_type'), {
	'html': pokemon_types_html,
    });
    if (is_authenticated) {
	$('#freeModal').on('hidden.bs.modal', function () {
	    if (pokemons_to_reload.length > 0) {
		$.get('/ajax/pokemons/?ids=' + pokemons_to_reload.join(',') + '&page_size=' + pokemons_to_reload.length, function(data) {
		    var html = $(data);
		    html.find('.pokemon').each(function() {
			$('#' + $(this).prop('id')).html($(this).html());
		    });
		    updatePokemons();
		    pokemons_to_reload = [];
		});
	    }
	})
    }
    if (typeof get_started != 'undefined' && get_started == true) {
	$('.total-search-results').hide();
    }
});
