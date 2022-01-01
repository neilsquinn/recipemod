import React, { useState, useEffect } from "react";
import axios from "axios";

import AddRecipeBox from "./components/AddRecipeBox.js";
import SearchBox from "./components/SearchBox.js";
import RecipeCardColumns from "./components/RecipeCardColumns.js";

function RecipeList() {
  const [recipes, setRecipes] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [parseErrorUrl, setParseErrorUrl] = useState(null);
  const [filteredRecipes, setFilteredRecipes] = useState([]);

  const [addRecipeUrlText, setAddRecipeURLText] = useState("");
  const [nameFilterText, setNameFilterText] = useState("");
  const [siteFilterText, setSiteFilterText] = useState("");

  useEffect(() => {
    setIsLoading(true);
    axios.get("/api/recipes").then((resp) => {
      setRecipes(resp.data.recipes);
      setFilteredRecipes(resp.data.recipes);
      setIsLoading(false);
    });
  }, []);
  // should it pass in the recipes array instead?
  function handleNameFilterChange(event) {
    const filterText = event.target.value;
    setNameFilterText(filterText);

    if (filterText) {
      setFilteredRecipes(
        recipes.filter(
          (recipe) =>
            recipe.name.toLowerCase().search(filterText.toLowerCase()) > -1
        )
      );
    } else {
      setFilteredRecipes(recipes);
    }
  }

  function handleSiteFilterChange(event) {
    const filterText = event.target.value;
    setSiteFilterText(filterText);
    if (filterText) {
      setFilteredRecipes(recipes.filter(
        (recipe) => new URL(recipe.url).host.search(filterText.toLowerCase()) > -1
      ));
    } else {
      setFilteredRecipes(recipes)
    }
  }

  function handleAddURLChange(event) {
    setAddRecipeURLText(event.target.value);
  }

  function handleSubmitRecipe(event) {
    let url = addRecipeUrlText;
    axios.post("/api/recipes/add", { url: url }).then((resp) => {
      const data = resp.data;
      console.log(data);
      if (data.hasOwnProperty("error")) {
        console.log("found parse error");
        setParseErrorUrl(url);
      } else {
        setRecipes([data.recipe].concat(recipes));
      }
    });
    event.preventDefault();
  }

  function handleFilterReset() {
    setSiteFilterText("");
    setNameFilterText("");
    setFilteredRecipes(recipes);
  }

  if (isLoading) {
    return (
      <div className="spinner-border text-danger" role="status">
        <span className="sr-only">Loading...</span>
      </div>
    );
  }

  return (
    <div>
      <h1 className="display-4">Recipes</h1>
      <AddRecipeBox
        handleAddURLChange={handleAddURLChange}
        handleSubmitRecipe={handleSubmitRecipe}
      />
      {parseErrorUrl ? (
        <div className="alert alert-danger alert-dismissible">
          <button
            type="button"
            className="close"
            data-dismiss="alert"
            onClick={() => setParseErrorUrl(null)}
          >
            &times;
          </button>
          <strong>Unable to add recipe:</strong> This page on{" "}
          {new URL(parseErrorUrl).hostname} does not contain a recipe in a
          format that RecipeMod can read.
        </div>
      ) : null}
      <SearchBox
        nameFilterText={nameFilterText}
        siteFilterText={siteFilterText}
        handleNameFilterChange={handleNameFilterChange}
        handleSiteFilterChange={handleSiteFilterChange}
        handleFilterReset={handleFilterReset}
      />
      <RecipeCardColumns recipes={filteredRecipes} />
    </div>
  );
}

export default RecipeList;
