import React, {Fragment} from "react";
import PropTypes from "prop-types";
import {Pencil, CheckCircle, XCircle} from "react-bootstrap-icons";


function EditorControls(props) {
	const iconStyles = {color: "DarkBlue", size: props.iconSize};
	console.log(props)
	if (props.isEditing) {
		return (
			<Fragment>
				<button type="submit" className='btn' title='Save'>
					<CheckCircle {...iconStyles} />
				</button>
				<button type="button" className='btn' title='Cancel' onClick={() => {
					props.setIsEditing(false)
					props.setEditedRecipe([])
				}}>
					<XCircle {...iconStyles} />
				</button>
			</Fragment>
		)
	} else {
		return (
			<button type="button" className='btn' title='Edit' onClick={() => props.setIsEditing(true)}>
				<Pencil {...iconStyles} />
			</button>
		) 
	}
}

EditorControls.propTypes = {
	// setIsEditing: PropTypes.func.isRequired,
	// setEditedRecipe: PropTypes.func.isRequired,
	// isEditing: PropTypes.bool.isRequired,
	iconSize: PropTypes.string,
}

EditorControls.defaultPropTypes = {
	iconSize: "1.2rem"
}

export default EditorControls