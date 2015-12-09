var webpack = require('webpack');

module.exports = {
    entry: './search.jsx',
    output: {
        //path: __dirname,
        filename: 'bundle.js', //this is the default name, so you can skip it
        // DEV
        // publicPath: 'http://localhost:8090/assets'
    },
    module: {
        loaders: [
            {
                test: /\.jsx?$/,
                loader: 'jsx-loader',
                exclude: /node_modules/
            },
        ]
    },
    externals: {
        // 'react': 'React'
    },
    resolve: {
        extensions: ['', '.js', '.jsx']
    },

    plugins: [
        new webpack.DefinePlugin({
        'process.env': {
          'NODE_ENV': JSON.stringify('production'),
        }
      }),
        new webpack.optimize.UglifyJsPlugin()
        ],
}