const path = require("path");

module.exports = {
  /*
   ** Headers of the page
   */
  head: {
    title: "Engster",
    meta: [{
        charset: "utf-8"
      },
      {
        name: "viewport",
        content: "width=device-width, initial-scale=1"
      },
      {
        hid: "description",
        name: "description",
        content: "Learn Real English with Engster!"
      }
    ],
    link: [{
      rel: "icon",
      type: "image/x-icon",
      href: "/favicon.ico"
    }]
  },
  modules: [
    ['@nuxtjs/dotenv', {
      filename: process.env.NODE_ENV !== 'production' ? '.env.dev' : '.env.prod'
    }],
  ],
  css: ["@/assets/scss/main.scss"],
  loading: {
    color: "#3B8070"
  },
  /*
   ** Build configuration
   */
  build: {
    vendor: ['axios'],
    extend(config, {
      isDev,
      isClient
    }) {
      if (isDev && isClient) {
        config.module.rules.push({
          enforce: "pre",
          test: /\.(js|vue)$/,
          loader: "eslint-loader",
          exclude: /(node_modules)/
        });
      }
      config.resolve.alias["~styles"] = path.join(__dirname, "assets/scss");
    }
  }
};
