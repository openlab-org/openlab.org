

openlab.register('docviewer', function () {
    var types = {};

    types.svgpan = function () {
        var url = $div.attr('data-svgpan-url');
        $.get(url, function (data) {
            var imported = document.importNode(data.documentElement, true);
            var $ndiv = $('<div id="svg_pan_viewport"></div>');
            $div.after($ndiv);
            $div.remove();
            $ndiv.append(imported);
            var svg = imported;
            var elem = svg.getElementsByTagName('g')[0]
            if (!elem.id) {
                elem.id = "openlab_docviewer_viewport";
            }

            $('svg').svgPan(elem.id)
        });
    };

    var viewerjs_template = 
            window.TinyTiny(['<iframe',
                'src="{{ url.static }}/viewerjs/index.html#{{ url.media }}{{ url.path }}"',
                'width="100%" height="500px"',
                'allowfullscreen webkitallowfullscreen></iframe>'].join(' '));

    types.viewerjs = function (opts) {
        return $(viewerjs(opts));
    };


    var setup = function ($div) {
        var attr = function (s) { return $div.attr(s); };
        var type = attr('viewer');
        var opts = {
            urls: {
                media: attr('url-media'),
                static: attr('url-static'),
                path: attr('url-path'),
            }
        };

        $div.on('click', function () {
            $div.off('click');
            var $result = types[type]($div);
            $div.replace($result);
        });
    };

    return setup;
});


openlab.register('svgpan', function () {

    var find_child = function (svg, depth) {
        if (!depth) {
            if (depth > 100) {
                throw "Too deep, giving up on pan!";
            }
        } else {
            depth = 1;
        }

        var children = svg.children;
        for (var i=0; i<children.length; i++) {
            var child = children[i];
            if (child.tagName === "g") {
                return child;
            } 
            /*else if (child.tagName !== "defs") {
                return find_child(child, depth+1);
            }*/
        }
        //return svg;

    };

    var setup = function ($div) {
        $div.on('click', function () {
            $div.off('click');
            var url = $div.attr('data-svgpan-url');
            $.get(url, function (data) {
                var imported = document.importNode(data.documentElement, true);
                var $ndiv = $('<div id="svg_pan_viewport"></div>');
                $div.after($ndiv);
                $div.remove();
                $ndiv.append(imported);
                window.i_svg = imported;
                var svg = imported;
                //var elem = svg.getElementsByTagName('g')[0]
                var elem = find_child(svg);
                if (!elem.id) {
                    elem.id = "openlab_docviewer_viewport";
                }
                //console.log("THSI IS ELEM", elem, elem.id);

                // TODO disabled since its not very good ATM
                //$ndiv.find('svg').svgPan(elem.id)
            });
        });
    };

    return setup;
});


