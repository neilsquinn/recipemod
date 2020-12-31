import React from "react";

function AddRecipeBox(props) {
  return (
    <form onSubmit={props.handleSubmitRecipe} className="needs-validation mb-3">
        <div className="form-group">
            <input type="url" onChange={props.handleAddURLChange} className="form-control form-control-lg" placeholder="Enter link to recipe" name="url" required></input>
        </div>
        <button type="submit" className="btn btn-primary">Add Recipe</button>
    </form>
  )
}

export default AddRecipeBox;