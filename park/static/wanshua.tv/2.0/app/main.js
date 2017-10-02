import Arg from 'script!../third-part/arg.js/arg-1.3.min'
import jQuery from 'script!../third-part/jquery/jquery.min'
import Cookies from 'script!../third-part/js-cookie/js.cookie'
import moment from 'script!../third-part/moment/moment-with-locales.min'
import _ from 'script!../third-part/lodash/lodash.min'
import lightSlider from 'script!../third-part/lightslider/js/lightslider.min'
import lightGallery from 'script!../third-part/lightgallery/js/lightgallery-all.min'

// Init
import Init from 'script!./_init_'
import utils from './utils'

import Vue from 'vue'

// vueConfig

Vue.config.debug = true;

Vue.prototype.$utils = utils;

Vue.use(require('vue-resource'));

Vue.filter('from_now', function(_date) {
    return utils.from_now.get_time(_date);
});

// Main

import App from '../src/App.vue'
import mIndex from '../src/mIndex.vue'

/* eslint-disable no-new */
new Vue({
    el: 'body',
    data: $DATA,
    components: {
        App, mIndex
    }
});
