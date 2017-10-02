var webpack = require('webpack');
var path = require('path');

var hotReplacePlugin = new webpack.HotModuleReplacementPlugin();
var commonsPlugin = new webpack.optimize.CommonsChunkPlugin('common.js');

module.exports = {
    debug: true,
    devtool: '#eval-source-map',
    context: path.join(__dirname, 'app'),

    entry: [
        'webpack/hot/dev-server',
        'webpack-hot-middleware/client',
        './main.js'
    ],
    output: {
        path: path.join(__dirname, 'dist'),
        publicPath: '/static/2.0/dist/',
        filename: '[name].js'
    },
    plugins: [
        hotReplacePlugin,
        commonsPlugin
    ],
    module: {
        loaders: [{
            test: /\.vue$/,
            loader: 'vue'
        }, {
            test: /\.js$/,
            // excluding some local linked packages.
            // for normal use cases only node_modules is needed.
            exclude: /node_modules|third-part|vue\/dist|vue-router\/|vue-loader\/|vue-hot-reload-api\//,
            loader: 'babel'
        }, {
            test: /\.scss$/,
            loaders: ["style", "css", "sass"]
        }, {
            test: /\.(png|jpg|gif)$/,
            loader: 'url',
            query: {
                limit: 10000,
                name: '[name].[ext]?[hash]'
            }
        }, {
            test: /\.(ttf|eot|svg|woff(2)?)(\?.+)?$/,
            loader: 'file-loader'
        }]
    },
    babel: {
        presets: ['es2015'],
        plugins: ['transform-runtime']
    }
}

if (process.env.NODE_ENV === 'production') {
    module.exports.entry = [
        './main.js'
    ];
    module.exports.plugins = [
        new webpack.DefinePlugin({
            'process.env': {
                NODE_ENV: '"production"'
            }
        }),
        new webpack.optimize.UglifyJsPlugin({
            compress: {
                warnings: false
            }
        }),
        new webpack.optimize.OccurenceOrderPlugin(),
        commonsPlugin
    ];
} else {
    module.exports.devtool = '#source-map'
}
