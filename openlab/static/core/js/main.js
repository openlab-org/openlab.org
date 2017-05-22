

var openlab = {};


openlab.autofield = function () {
    var funcs = {
        slug: function (value) {
            return value.replace(/[\W_-]+/g, '-')
                    .toLowerCase()
                    .replace(/-+$/, '')
                    .replace(/^-+/, '');
        },
        'location': function (value) {
            // TODO need to think through -- this will do reverse GEO lookup
            // stuff from an address field
        }
    };

    var READONLY = 'readonly';

    $('[data-autofield]').each(function() {
        var $e = $(this);
        var target = $e.attr('data-autofield');
        var operation = funcs[$e.attr('data-operation') || 'slug'];

        // Search for target within parent form
        var $target = $($e.parents('form').find('[name='+target+']')[0]);
        $e.attr(READONLY, READONLY);

        $target.on('keyup', function () {
            $e.val(operation($target.val()));
        });
        $target.trigger('keyup');

        if (!$e.attr('data-disallow-direct')) {
            var $force_edit = $('<label><input type="checkbox" /><i class="icon-edit"></i></label>')
                .tooltip({
                    html: "<p>Edit this field manually.</p><p><small>Note: "+
                    "It's recommended you let it be set automatically.</small></p>"
                })
                .css({
                    display: 'inline-block',
                    position: 'absolute',
                    left: 20,
                    top: 5,
                })
                .find('input').change(function () {
                    if ($(this).prop('checked')) {
                        $e.removeAttr(READONLY);
                    } else {
                        $e.attr(READONLY, READONLY);
                    }
                }).end();
            $e.css('padding-left', 50);
            $e.before($force_edit)
        };
    });
};

openlab.olmdtextarea = function () {
    // TODO move this into the olmarkdown view
    $('textarea[data-olmarkdown]').each(function () {
        var $el = $(this);
        var users = $(this).attr('data-users');
        if (users) {
            $(this).atwho({
                at: '@',
                data: JSON.parse(users)
            });   
        }

        $(this).autosize();
        $(this).markdown({
            hiddenButtons: ["cmdImage", "cmdPreview"]
            /*,
            onPreview: function (a) {
                a('asdf');
                return function () {
                    return "lolol"
                }
            }
            */
        });
    });
};

openlab.modules = {};
openlab.views = {};
openlab.register = function (name, func) {
    openlab.modules[name] = func;
};

openlab.main = function () {
    // Add in tool tips
    $('.tip').tooltip();

    // add in auto-fields (ie slug generation)
    openlab.autofield();

    // add in olmarkdown fields
    openlab.olmdtextarea();

    // detect touch-able
    if ("ontouchstart" in document.documentElement) {
        document.documentElement.className += " touch";
    } else {
        document.documentElement.className += " no-touch";
    }

    // And now we do all the views
    $('[data-jsview]').each(function () {
        var $e = $(this);
        var view_name = $e.attr('data-jsview');
        if (!openlab.views[view_name]) {
            console.log("setting up", view_name);
            if (openlab.modules[view_name]) {
                // instantiate module
                openlab.views[view_name] = openlab.modules[view_name]();
            } else {
                console.error("Could not find js view", view_name);
            }
        }
        openlab.views[view_name]($e);
    });
};

$(document).ready(openlab.main);

