import React from "react";
import RecipeCard from './RecipeCard.js';

function RecipeCardColumns(props) {
  const recipeCards = props.recipes.map((recipe) => 
    <RecipeCard key={recipe.id} recipe={recipe}/>
  );
  return <div id="recipe-cards" className="row row-cols-1 row-cols-md-3 g-4">
  {recipeCards}
  </div>
}

export default RecipeCardColumns