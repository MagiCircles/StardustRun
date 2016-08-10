
function changePokedex(pokedex, data) {
    if (typeof data['error'] != 'undefined') {
	alert(data['error']);
	return
    }
    var form = pokedex.find('form.candiesform');
    $.each(data['updated'], function(_, id) {
	var each_form;
	if ($('.profile-account').length > 0) {
	    each_form = pokedex.closest('.profile-account').find('.full-pokemon-pokedex[data-pokemon="' + id + '"] .candiesform');
	} else {
	    each_form = $('.full-pokemon-pokedex[data-pokemon="' + id + '"] .candiesform');
	}
	var input = each_form.find('input[name="candies"]');
	input.val(data['candies']);
	if (data['candies'] > 0) {
	    each_form.find('img.without-background').hide();
	    each_form.find('img.with-background').show();
	} else {
	    each_form.find('img.with-background').hide();
	    each_form.find('img.without-background').show();
	}
    });
    pokedex.find('.change-seen').removeClass('flaticon-loading');
    if (data['seen']) {
	pokedex.find('.change-seen').removeClass('flaticon-delete');
	pokedex.find('.change-seen').addClass('flaticon-checked');
	pokedex.find('.pokemon-image').removeClass('not-seen');
    } else {
	pokedex.find('.change-seen').removeClass('flaticon-checked');
	pokedex.find('.change-seen').addClass('flaticon-delete');
	pokedex.find('.pokemon-image').addClass('not-seen');
    }
    pokedex.find('.change-caught').removeClass('flaticon-loading');
    if (data['caught']) {
	pokedex.find('.change-caught').removeClass('flaticon-delete');
	pokedex.find('.change-caught').addClass('flaticon-checked');
    } else {
	pokedex.find('.change-caught').removeClass('flaticon-checked');
	pokedex.find('.change-caught').addClass('flaticon-delete');
    }
}

function changePokedexBoolean(button, to_change, change_to) {
    var pokedex = button.closest('.full-pokemon-pokedex');
    if (!pokedex.hasClass('not-editable-pokedex')) {
	var account = pokedex.data('account');
	var pokemon = pokedex.data('pokemon');
	var data = {};
	data[to_change] = change_to;
	$.ajax({
	    type: "POST",
	    url: '/ajax/change_' + to_change + '/' + pokemon + '/' + account + '/',
	    data: data,
	    success: function(data) {
		changePokedex(pokedex, data);
	    },
	    error: genericAjaxError,
	});
    } else {
	window.location.href = pokedex.closest('a').prop('href');
    }
}

$(document).ready(function() {
    // Add to the list of pokemons to reload to keep parent view consistent
    if (typeof pokemons_to_reload != 'undefined') {
	var id = $('.full-pokemon').data('full-pokemon-id');
	if (pokemons_to_reload.indexOf(id) == -1) {
	    pokemons_to_reload.push(id);
	}
    }

    loadToolTips();
    $('[data-toggle="popover"]').popover();
    $('input[name="candies"]').change(function() {
	$(this).closest('form').find('input[type="submit"]').show();
    });
    $('.candiesform').unbind('submit');
    $('.candiesform').submit(function(e) {
	e.preventDefault();
	var form = $(this);
	var pokedex = form.closest('.full-pokemon-pokedex');
	var loading = form.find('.flaticon-loading');
	var button = form.find('input[type="submit"]');
	loading.show();
	button.hide();
	form.ajaxSubmit({
	    success: function(data) {
		loading.hide();
		button.hide();
		changePokedex(pokedex, data);
	    },
	    error: genericAjaxError,
	});
	return false;
    });
    $('.pokemon-image-change-seen').unbind('click');
    $('.pokemon-image-change-seen').click(function(e) {
	e.preventDefault();
	changePokedexBoolean($(this), 'seen', $(this).hasClass('not-seen'));
	return false;
    });
    $('.change-seen').unbind('click');
    $('.change-seen').click(function(e) {
	e.preventDefault();
	changePokedexBoolean($(this), 'seen', !$(this).hasClass('flaticon-checked'));
	return false;
    });
    $('.change-caught').unbind('click');
    $('.change-caught').click(function(e) {
	e.preventDefault();
	changePokedexBoolean($(this), 'caught', !$(this).hasClass('flaticon-checked'));
	return false;
    });
    $('.full-pokemon a[href="#addPokemon"]').unbind('click');
    $('.full-pokemon a[href="#addPokemon"]').click(function(e) {
	e.preventDefault();
	var button = $(this);
	var collection = button.closest('.pokemons-collection');
	var form = collection.find('form');
	var loader = collection.find('.flaticon-loading');
	button.hide();
	loader.show();
	form.ajaxSubmit({
	    success: function(data) {
		freeModal($('#freeModal .modal-header h4').text(), data);
		// Add all ownedpokemons to reload
		if (typeof ownedpokemons_to_reload != 'undefined') {
		    $('.full-pokemon .ownedpokemon').each(function() {
			var id = $(this).data('ownedpokemon-id');
			if (ownedpokemons_to_reload.indexOf(id) == -1) {
			    ownedpokemons_to_reload.push(id);
			}
		    });
		}
	    },
	});
	return false;
    });
    ajaxModals();
});
