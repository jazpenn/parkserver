(function(global, factory) {
    typeof exports === 'object' && typeof module !== 'undefined' ? module.exports = factory() :
        typeof define === 'function' && define.amd ? define(factory) :
        global.utils = factory()
}(this, function() {
    'use strict';

    var utils = {};

    // FromNow
    moment.locale('zh-cn');
    utils.from_now = {

        get_time: function(_date) {
            var _time = moment(_date).fromNow();
            return _time;
        }

    };

    utils.$ = $;
    utils._ = _;

    utils.update = _.partialRight(_.assign, function(objectValue, sourceValue) {
        return (_.isNull(sourceValue) || _.isUndefined(sourceValue)) ? sourceValue : objectValue;
    });

    return utils;
}));
