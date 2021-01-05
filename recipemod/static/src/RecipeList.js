import React, {useState, useEffect} from 'react';
import axios from 'axios';

import AddRecipeBox from './components/AddRecipeBox.js';
import SearchBox from './components/SearchBox.js';
import RecipeCardColumns from './components/RecipeCardColumns.js';


function RecipeList() {

  const [recipes, setRecipes] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    console.log('get recipes');
    setIsLoading(true);
    axios.get("/api/recipes")
     .then(resp => {
        setRecipes(resp.data.recipes);
        setIsLoading(false);
      });
  }, []); 
  // should it pass in the recipes array instead?
  const [nameFilterText, setNameFilterText] = useState('');
  function handleNameFilterChange(event) {
     setNameFilterText(event.target.value);
  }
  if (nameFilterText) {
    let lowerFilterText = nameFilterText.toLowerCase();
    recipes = recipes.filter(recipe => recipe.name.toLowerCase().search(lowerFilterText) > -1);
  }

  const [addRecipeUrlText, setAddRecipeURLText] = useState('');
  function handleAddURLChange(event) {
    setAddRecipeURLText(event.target.value);
  }

  const [siteFilterText, setSiteFilterText] = useState('');
  function handleSiteFilterChange(event){
    setSiteFilterText(event.target.value);
  }
  if (siteFilterText) {
    let lowerFilterText = siteFilterText.toLowerCase();
    recipes = recipes.filter(recipe => recipe.domain.search(lowerFilterText) > -1);
  }

  function handleSubmitRecipe(event) {
    let url = addRecipeUrlText;
    axios.post('/api/recipes/add', {url: url})
      .then((resp) => {
        setRecipes([resp.data.recipe].concat(recipes));
      });
    event.preventDefault();
  }

  function handleFilterReset() {
    setSiteFilterText('');
    setNameFilterText('');
  }  

  if (isLoading) {
    return (
      <div className="spinner-border text-danger" role="status">
        <span className="sr-only">Loading...</span>
      </div>
    )
  }

  return (
    <div>
      <h1 className="display-4">Recipes</h1>
      <AddRecipeBox 
        handleAddURLChange={handleAddURLChange}
        handleSubmitRecipe={handleSubmitRecipe} 
      />
      <SearchBox nameFilterText={nameFilterText} 
        siteFilterText={siteFilterText}
        handleNameFilterChange={handleNameFilterChange} 
        handleSiteFilterChange={handleSiteFilterChange}
        handleFilterReset={handleFilterReset}
      />
      <RecipeCardColumns recipes={recipes} />
    </div>
  )
}

export default RecipeList