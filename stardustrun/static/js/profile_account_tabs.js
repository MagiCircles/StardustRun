
function reloadOwnedPokemonsAfterModal() {
    if (is_authenticated) {
	$('#freeModal').on('hidden.bs.modal', function () {
	    if (ownedpokemons_to_reload.length > 0) {
		$.get('/ajax/ownedpokemons/?back_to_profile&ids=' + ownedpokemons_to_reload.join(',') + '&page_size=' + ownedpokemons_to_reload.length, function(data) {
		    var html = $(data);
		    // Remove all that weren't returned
		    $.each(ownedpokemons_to_reload, function(_, id) {
			if (html.find('[data-ownedpokemon-id="' + id + '"]').length == 0) {
			    $('[data-ownedpokemon-id="' + id + '"]').after('<br><br><span class="text-muted">' + gettext('Deleted') + '</span><br><br>');
			    $('[data-ownedpokemon-id="' + id + '"]').remove();
			}
		    });
		    html.find('.ownedpokemon').each(function() {
			var newOwnedpokemonItem = $(this);
			var ownedpokemonItem = $('.profile-account #' + newOwnedpokemonItem.prop('id'));
			if (ownedpokemonItem.length > 0) {
			    // Replace existing
			    ownedpokemonItem.html(newOwnedpokemonItem.html());
			} else {
			    // Add at the end
			    var account_id = newOwnedpokemonItem.data('ownedpokemon-account-id');
			    var newElement = $('<div class="col-sm-3"></div>');
			    newElement.html(newOwnedpokemonItem);
			    $('#account' + account_id + 'Pokemons .row').last().append(newElement);
			}
		    });
		    ownedpokemons_to_reload = [];
		    ajaxModals();
		    loadToolTips();
		});
	    }
	})
    }
}

function loadPokedex(pane, account, parameters) {
    parameters = typeof parameters == 'undefined' ? '' : parameters;
    pane.html('<i class="flaticon-loading"></i>');
    $.get('/ajax/pokedex/' + account.data('account-id') + '/' + parameters, function(data) {
	pane.html(data);
	loadToolTips();
	$('[href="#changeToIcons"]').click(function(e) {
	    e.preventDefault();
	    loadPokedex(pane, account, '?view=icons');
	    return false;
	});
	$('[href="#changeToList"]').click(function(e) {
	    e.preventDefault();
	    loadPokedex(pane, account, '?view=list');
	    return false;
	});
    });
}

function loadPokemons(pane, account) {
    pane.html('<i class="flaticon-loading"></i>');
    var account_id = account.data('account-id');
    $.get('/ajax/ownedpokemons/?account=' + account_id + '&ajax_modal_only&back_to_profile', function(data) {
	if (data.trim() == '') {
	    pane.html('<div class="padding20"><div class="alert alert-warning">' + gettext('No result.') + '</div></div>');
	} else {
	    pane.html('<br><a href="' + window.location.pathname + '?account' + account_id + '=Pokemons#' + account_id + '" class="btn-pokemon" data-toggle="tooltip" title="' + gettext('Permalink') + '"><i class="flaticon-link"></i></a>' + data);
	    loadToolTips();
	    ajaxModals();
	}
    });
}

function onTabChanged(target_name, pane) {
    if (pane.text() == '') {
	var account = pane.closest('.profile-account');
	if (target_name.match(/Pokemons$/)) {
	    loadPokemons(pane, account);
	} else if (target_name.match(/Pokedex$/)) {
	    loadPokedex(pane, account);
	}
    }
}

function levelUpButtons() {
    $('.form-level-up').submit(function(e) {
	e.preventDefault();
	var form = $(this);
	form.ajaxSubmit({
	    success: function(data) {
		var account = form.closest('.profile-account');
		account.find('.level .level-value').text(data['level']);
		account.find('.ranking-global .value').text(data['leaderboard']);
		account.find('.ranking-team .value').text(data['leaderboard_team']);
	    },
	    error: genericAjaxError,
	});
	return false;
    });
}

$(document).ready(function() {
    $('.profile-account .tab-pane.active').each(function() {
	onTabChanged($(this).prop('id'), $(this));
    });
    $('.profile-account .nav-tabs > li a').on('show.bs.tab', function(e) {
	var target_name = $(e.target).attr('href');
	var pane = $(target_name);
	onTabChanged(target_name, pane);
    });
    reloadOwnedPokemonsAfterModal();
    levelUpButtons();
});
