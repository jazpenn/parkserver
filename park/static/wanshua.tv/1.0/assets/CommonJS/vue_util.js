


_util = {};

_util.update = function (obj, _obj) {
    for (var key in _obj)
        if (_obj[key]!=null) obj[key] = _obj[key];
};

module.exports = _util;


// ------ Else ------


// VueSet
Vue.config.delimiters = ["[[", "]]"];


// VueBind

VueBind = {
    _attr_: 'vue-bind',
    _do_vue_: function($el){

        _vue = new Vue({
            el: $el[0],
            data: function(){
                return $el.data();
            }
        });

        return _vue;
    },
    _init_: function(){

        var that = this;

        $('[' + that._attr_ + ']').each(function(){

            var _this = $(this);

            that._do_vue_(_this);

        });
    }
};
