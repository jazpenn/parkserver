// Init mdl-tab
$(document).on('click', '.uri-link', function(e) {
    var uri = $(this).attr('uri');
    var url = Arg.url(window.location.pathname, {
        uri: uri
    });
    history.replaceState(null, null, url);
});
