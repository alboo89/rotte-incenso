module.exports = function (eleventyConfig) {
  // Asset statici copiati cosi' come sono
  eleventyConfig.addPassthroughCopy({ "src/assets": "assets" });
  eleventyConfig.addPassthroughCopy({ "src/admin": "admin" });
  eleventyConfig.addPassthroughCopy({ "src/robots.txt": "robots.txt" });

  // Le destinazioni ordinate per campo "ordine"
  eleventyConfig.addCollection("destinazioni", function (api) {
    return api.getFilteredByGlob("src/destinazioni/*.md")
      .sort((a, b) => (a.data.ordine || 99) - (b.data.ordine || 99));
  });

  return {
    dir: { input: "src", includes: "_includes", data: "_data", output: "_site" },
    htmlTemplateEngine: "njk",
    markdownTemplateEngine: "njk"
  };
};
