import React from 'react';
import {Link} from "react-router-dom";

function RecipeCard(props) {
  const recipe = props.recipe;
  return (
    <div className="card shadow-sm">
    {recipe.image_url 
      ? <img className="card-img-top" src={recipe.image_url} alt="Recipe image"></img>
      : null
    }
    <div className="card-body">
      <h5 className="card-title">
      <span className="recipe-name">{recipe.name}</span> 
      <span className="text-secondary small recipe-domain"> ({new URL(recipe.url).hostname})</span></h5>
      <p className="card-text font-italic small">
      {recipe.description && recipe.description.length > 150 
        ? recipe.description.slice(0, 150).trim() + "..." 
        : recipe.description
      }
      </p>
      <Link className="btn btn-primary stretched-link" to={`/recipe/${recipe.id}`}>View</Link>
      </div>
    </div>
    );
}

export default RecipeCard;