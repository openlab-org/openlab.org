
openlab.register('release_preview_pane', function () {
    var refresh = function ($pane, $form) {
    };

    var setup = function ($el) {
        /* set up form info */
        var $form = $el.parents('form');
        var $pane = $($el.attr('href'));
        var target_url =  $el.attr('data-release-preview-url');

        var do_refresh = function () {
            refresh($pane, $form);
        };

        $el.on('shown.bs.tab', do_refresh);
    };
    return setup;
});
