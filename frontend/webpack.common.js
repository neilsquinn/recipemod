const path = require("path");

const staticDirPath = path.resolve(__dirname, "../recipemod/static/dist");

module.exports = {
  devtool: "inline-source-map",
  entry: {
    index: "./src/index.js",
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
  output: {
    path: staticDirPath,
    clean: true,
  },
};
