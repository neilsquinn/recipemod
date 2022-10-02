const path = require("path");
const { CleanWebpackPlugin } = require("clean-webpack-plugin");

const staticDirPath = path.resolve(__dirname, "./recipemod/static");

module.exports = {
  mode: "development",
  entry: {
    index: path.resolve(staticDirPath, "src/index.js"),
  },
  devServer: {
    contentBase: path.resolve(staticDirPath, "dist"),
    hot: true,
    proxy: {
      "/api": "http://localhost:5000",
    },
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        loader: "babel-loader",
        options: {
          presets: ["@babel/preset-env", "@babel/preset-react"], // ?
        },
      },
      {
        test: /\.css/,
        use: ["style-loader", "css-loader"],
      },
    ],
  },
  devtool: "inline-source-map",
  plugins: [new CleanWebpackPlugin()],
  output: {
    filename: "bundle.js",
    path: path.resolve(staticDirPath, "dist"),
  },
};
