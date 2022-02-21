import React from "react";

function AddRecipeBox(props) {
  const {loading} = props
  return (
    <form onSubmit={props.handleSubmitRecipe} className="needs-validation mb-3">
      <div className="form-group">
        <input type="url" onChange={props.handleAddURLChange} className="form-control form-control-lg" placeholder="Enter link to recipe" name="url" required></input>
      </div>
       <button type="submit" className="btn btn-primary">Add Recipe {loading ? <span className="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> : null}</button>
    </form>
  )
}

export default AddRecipeBox;