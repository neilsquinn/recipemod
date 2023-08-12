import React, { useState } from "react";
import PropTypes from "prop-types";
import { Pencil, CheckCircle, XCircle } from "react-bootstrap-icons";

function ToggleableEditor(props) {
  const [isEditing, setIsEditing] = useState(false);

  const iconStyles = { color: "DarkBlue", size: "1.2rem" };
  const headerElem = <h3 style={{ display: "inline-block" }}>{props.title}</h3>;

  function handleSubmit(event) {
    event.preventDefault();
    console.log("handling submit");
    props.setEditSaved(true);
    setIsEditing(false);
  }

  if (isEditing) {
    return (
      <form onSubmit={handleSubmit}>
        {headerElem}
        <button type="submit" className="btn" title="Save">
          <CheckCircle {...iconStyles} />
        </button>
        <button
          type="button"
          className="btn"
          title="Cancel"
          onClick={() => {
            setIsEditing(false);
            props.setEditedRecipe([]);
          }}
        >
          <XCircle {...iconStyles} />
        </button>
        {props.renderEditFunc()}
      </form>
    );
  } else {
    return (
      <div>
        {headerElem}
        <button
          type="button"
          className="btn"
          title="Edit"
          onClick={() => setIsEditing(true)}
        >
          <Pencil {...iconStyles} />
        </button>
        {props.renderViewFunc()}
      </div>
    );
  }
}

ToggleableEditor.propTypes = {
  title: PropTypes.string.isRequired,
  renderViewFunc: PropTypes.func.isRequired,
  renderEditFunc: PropTypes.func.isRequired,
  setEditSaved: PropTypes.func.isRequired,
  setEditedRecipe: PropTypes.func.isRequired,
};

export default ToggleableEditor;
