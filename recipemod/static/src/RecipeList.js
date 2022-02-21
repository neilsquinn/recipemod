import React, { useState, useEffect } from "react";
import axios from "axios";

import AddRecipeBox from "./components/AddRecipeBox.js";
import SearchBox from "./components/SearchBox.js";
import RecipeCardColumns from "./components/RecipeCardColumns.js";
import { states } from "./constants.js";

function RecipeList() {
  const [recipes, setRecipes] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [submitStatus, setSubmitStatus] = useState(states.INIT);
  const [submitErrorMessage, setSubmitErrorMessage] = useState("");
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
      setFilteredRecipes(
        recipes.filter(
          (recipe) =>
            new URL(recipe.url).host.search(filterText.toLowerCase()) > -1
        )
      );
    } else {
      setFilteredRecipes(recipes);
    }
  }

  function handleAddURLChange(event) {
    setAddRecipeURLText(event.target.value);
  }

  function handleSubmitRecipe(event) {
    let url = addRecipeUrlText;
    setSubmitStatus(states.LOADING);
    axios
      .post("/api/recipes/add", { url: url })
      .then((resp) => {
        const data = resp.data;
        const newRecipes = [data.recipe].concat(recipes);
        setRecipes(newRecipes);
        setFilteredRecipes(newRecipes);
        setSubmitStatus(states.COMPLETE);
      })
      .catch((err) => {
        setSubmitStatus(states.ERROR);
        const errorType = err.response.data.error;
        const errorMessage = errorMessages[errorType];
        if (errorMessage) {
          setSubmitErrorMessage(errorMessage);
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

  const errorMessages = {
    MISSING_URL: "Please provide a valid URL.",
    REQUEST_FAILED: "Unable to load data from this page.",
    PARSE_FAILED: "Unable to extract a recipe from this page.",
  };

  return (
    <div>
      <h1 className="display-4">Recipes</h1>
      <p>Status: {submitStatus}</p>
      <AddRecipeBox
        handleAddURLChange={handleAddURLChange}
        handleSubmitRecipe={handleSubmitRecipe}
        loading={submitStatus == states.LOADING}
      />
      {submitStatus == states.ERROR ? (
        <div className="alert alert-danger alert-dismissible">
          <button
            type="button"
            className="close"
            data-dismiss="alert"
            onClick={() => {
              setSubmitStatus(states.INIT);
              setSubmitErrorMessage("");
            }}
          >
            &times;
          </button>
          <strong>Unable to add recipe:</strong>
          {submitErrorMessage}
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
