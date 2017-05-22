
openlab.register('component_manager', function () {

    var _uuid=10000, uuid = function () { return "newc_"+(_uuid++); };

    var html_clone = function ($e) {
        return $('<div></div>').html($e.clone()).html();
    };

    var serialize_manager = function ($manager) {
        /*
         * Serializes into JSON object.
         */
        var list = [];
        $manager.find('[data-component]').each(function () {
            var $c = $(this);

            /* create file list */
            var file_list = [];
            $c.find('[data-file]').each(function () {
                var file_json = $(this).attr('data-filemodel-serialized') || '{}';
                file_list.push(JSON.parse(file_json));
            });

            /* push the component onto the list */
            list.push({
                id: $c.attr('data-component') || uuid(),
                title: $c.find('.c-title').val() || '',
                summary: $c.find('.c-summary').val() || '',
                files: file_list,
            });
        });

        return list;
    };

    var refresh = function ($manager) {
        // First refresh all empty placeholders
        $manager.find('[data-component]').each(function () {
            var $ph = $(this).find('.empty-placeholder');
            if ($(this).find('[data-file]').length > 0) {
                $ph.hide();
            } else {
                $ph.removeClass('hide');
                $ph.show();
            }
        });
    };

    var sync = function ($manager) {
        // Sync all to the give form tag
        var name = $manager.attr('data-component-manager');
        var $input = $('[name='+name+']');
        var obj = serialize_manager($manager);
        $input.val(JSON.stringify(obj));
        console.log("THIS IS VAL", $input.val());
    };

    var make_sortable = function ($manager, $e) {
        $e.sortable({
            items: "[data-file]",
            connectWith: "[data-component]",
            placeholder: "file-thumbnail",
            stop: function () {
                refresh($manager);
                sync($manager);
            }
        }).disableSelection();
    };

    var setup = function ($manager) {
        $manager.sortable({
                items: "[data-component]",
                handle: "p.component-handle",
                placeholder: "component-box placeholder",
                stop: function () {
                    sync($manager);
                }
            }).disableSelection();

        make_sortable($manager, $manager.find('[data-component]'));

        $manager.find('.new-component-button').click(function () {
            //var $component = $('[data-component]').first().clone();
            var $component = $(html_clone($('[data-component]').first()));
            $component.attr('data-component', uuid());
            $component.find('[data-file]').remove();
            $component.find('.c-summary').val('');
            $component.find('.c-title').val('');

            make_sortable($manager, $component);

            // insert after the last one
            $('[data-component]').last().after($component);

            refresh($manager);
        });

        // Finally refresh & sync up
        refresh($manager);
        sync($manager);
    };

    return setup;
});

