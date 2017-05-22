/*
 * PhantomJS script for rasterizing pages.
 */


///////////////////////////////////
// PHANTOMJS FUNCTIONS           //
///////////////////////////////////

var _extend = function (a, b) {
    for (var k in b) {
        a[k] = b[k];
    }
    return a;
};

var phantomjs_rastorize = function (options) {
    var page = require('webpage').create();

    var option_defaults = {
            // Resolution of headless browser
            resolution: {
                width: 1200,
                height: 700
            },

            // Most important thing: what part of the page do you really want
            crop: {
                'top': 0,
                left: 0,
                width: 1170,
                height: 585
            },

            // How long to account for page loading. Set to 'alert' to wait for
            // alert('phantom.ready'), or callback for 'window.callPhantom'
            // (not supported yet)
            //delay: 100,
            delay: 'alert',

            // Page zoom factor
            zoom: false,

            // Output file (Supported formats PNG GIF JPEG PDF)
            output: null,

            // Input file
            input: null,

            // Code to run
            code: null,

            // For PDF
            page: {
                height: '7.01in',
                width: '4.33in',
                //format: false,
                margin: '1cm',
                orientation: 'portrait'
            }
        };

    var opts = _extend(option_defaults, options);

    if (!opts.input || !opts.output) {
        console.error("No input specified!", opts.input);
        return;
    }
    var address = opts.input;

    // Absolute file path instead of URL
    if (address.indexOf('/') === 0) {
        address = 'file://' + address;
    }

    // PDF support ^_^
    if (opts.output.substr(-4) === ".pdf") {
        page.paperSize = opts.page;
    }

    // Zoom at all? Could be useful for retina version.
    if (opts.zoom) {
        page.zoomFactor = opts.zoom;
    }

    // apply clip
    if (opts.crop) {
        page.clipRect = opts.crop;
    }

    page.viewportSize = { width: opts.width, height: opts.height };

    page.open(address, function (status) {
        if (status !== 'success') {
            console.log('Unable to load the address!');
            phantom.exit();
        } else {
            if (opts.code) {
                eval(code);
            }
            window.setTimeout(function () {
                page.render(opts.output);
                phantom.exit();
            }, 100);
        }
    });
};


var phantomjs_main = function () {
    var system = require('system');
    var json_str = system.args.slice(1).join(' ');
    var json = JSON.parse(json_str);
    phantomjs_rastorize(json);
    return;
};

phantomjs_main();
