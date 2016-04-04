/**
 * Created by ama on 23/11/2015.
 */
var path = require('path');
module.exports = {
    entry: { app: "./src/index.js"},
    output: {
        path: path.resolve(__dirname, 'static'),
        filename: "[name]_bundle.js"
    },
    module: {
        loaders: [
            { test: /\.js$/, exclude: /node_modules/, loader: "babel-loader"}
        ]
    }
};