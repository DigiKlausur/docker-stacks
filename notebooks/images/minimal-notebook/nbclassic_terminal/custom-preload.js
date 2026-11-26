// e2x: open terminals from nbclassic in nbclassic's own terminal page.
// nbclassic links terminals to <base_url>/terminals/<name>, which Notebook 7 serves
// (its logo leads to /tree). Point "New -> Terminal" and the running-terminals list
// at <base_url>/nbclassic/terminals/<name>, served by the nbclassic_terminal server
// extension. Every nbclassic page loads this before its main.js runs, so the patch
// is in place before the tree page binds its buttons.
// Remove once e2xgrader runs on Notebook 7.
define([
    'base/js/namespace',
    'base/js/utils',
    'tree/js/terminallist'
], function (IPython, utils, terminallist) {
    "use strict";

    var proto = terminallist.TerminalList.prototype;

    var terminal_url = function (base_url, name) {
        return utils.url_path_join(base_url, 'nbclassic/terminals',
            utils.encode_uri_components(name));
    };

    // Upstream new_terminal with only the page URL changed.
    proto.new_terminal = function (event) {
        if (event) {
            event.preventDefault();
        }
        var w = window.open('#', IPython._target);
        var base_url = this.base_url;
        var settings = {
            type : "POST",
            dataType: "json",
            success : function (data) {
                w.location = terminal_url(base_url, data.name);
            },
            error : function (jqXHR, status, error) {
                w.close();
                utils.log_ajax_error(jqXHR, status, error);
            },
        };
        utils.ajax(utils.url_path_join(base_url, 'api/terminals'), settings);
    };

    var add_link = proto.add_link;
    proto.add_link = function (name, item) {
        add_link.apply(this, arguments);
        item.find("a.item_link").attr('href', terminal_url(this.base_url, name));
    };
});
