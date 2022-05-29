const production = !process.env.ROLLUP_WATCH
module.exports = {
  future: {
    purgeLayersByDefault: true,
    removeDeprecatedGapUtilities: true,
  },
  plugins: [
    require("daisyui")
  ],
  daisyui: {
    styled: true,
    themes: true,
    base: true,
    utils: true,
    logs: true,
    rtl: false,
    prefix: "",
    darkTheme: "dark",
  },
  content: [
    "./src/App.svelte",
  ],
  theme: {
    extend: {},
  },
}
