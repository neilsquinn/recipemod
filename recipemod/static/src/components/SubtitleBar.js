import React, { Fragment } from "react";

function SubtitleBar(props) {
  const recipe = props.recipe;

  return (
    <div className="small text-uppercase mb-3">
      <span className="font-weight-light">Added: </span>
      <span>{new Date(recipe.created).toLocaleDateString()} | </span>
      {recipe.updated ? (
        <Fragment>
          <span className="font-weight-light">Modified:</span>
          <span>{new Date(recipe.created).toLocaleDateString()} | </span>
        </Fragment>
      ) : null}
      {recipe.authors ? (
        <Fragment>
          <span className="font-weight-light">By: </span>
          <span>{recipe.authors.join(", ")} | </span>
        </Fragment>
      ) : null}
      <span className="font-weight-light">From: </span>
      <a href={recipe.url} target="_blank">
        {new URL(recipe.url).hostname}
      </a>
    </div>
  );
}

export default SubtitleBar;
