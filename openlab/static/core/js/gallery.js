
/*
 * Manage gallery view
 */
openlab.register('manage_gallery', function () {


    var main = function ($el) {
        $el.find('.btn-group .btn').tooltip({container: 'body'});

        $el.find('.btn.check-all').click(function () {
            var $boxes = $("[name=files]");
            $boxes.attr("checked", "checked");
        });

        $el.find('input[type=checkbox]').on('change', function () {
            var $input = $(this);
            var is_checked = !!$input.prop('checked');
            $input.parent()[
                is_checked ? 'addClass' : 'removeClass']('input-checked');
        });
    };

    return main;
});

