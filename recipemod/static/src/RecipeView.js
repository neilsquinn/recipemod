import React, {useState, useEffect, Fragment} from 'react';
import axios from 'axios';
import {useHistory} from "react-router-dom";
import {Pencil, CheckCircle, XCircle} from "react-bootstrap-icons";

import SubtitleBar from './components/SubtitleBar.js';
import InfoPanel from './components/InfoPanel.js';
import ToggleableEditor from './components/ToggleableEditor.js';

// TODO add onError for image- onError={(e) => e.target.src = some url} works if i have a placeholder 

function RecipeView(props) {
	const [recipe, setRecipe] = useState([]);
	const [isLoading, setIsLoading] = useState(true);
	const [editedRecipe, setEditedRecipe] = useState([])
	const [editSaved, setEditSaved] = useState(false);

	let history = useHistory();

	useEffect(() => {
		setIsLoading(true);
		console.log('loading recipe')
		axios.get(`/api/recipes/${props.recipeId}`)
			.then(resp => {
				const recipe = resp.data.recipe
				setRecipe(recipe);
				setIsLoading(false);
			})
			.catch(error => {
				console.log(error.response)
				if (error.response.status == 404) {
					alert('Recipe not found.')
				} else {
					alert('Unable to load recipe!')
				}
			});
	}, []);

	useEffect(() => {
		console.log('running edit effect, editSaved is:', editSaved)
		if (editSaved) {
			console.log('saving to server', editedRecipe)
			axios.put(`/api/recipes/${props.recipeId}`, {recipe: editedRecipe})
				.then(resp => {
					setRecipe(resp.data.recipe)
					setEditSaved(false)
					setEditedRecipe([])
				})
			
		}
		
	}, [editSaved]);

	function handleDelete(event) { 
		if (!confirm('Are you sure?')) {
			return null;
		}
		axios.delete(`/api/recipes/${props.recipeId}`)
			.then(resp => history.push("/"))
			.catch(error => alert('Unable to delete recipe!'));
		
	}

	function renderViewIngredients() {
		return (
			<ul>
			{
				recipe.ingredients.map((ingredient, index) => <li key={index}>{ingredient}</li>)
			}
			</ul>
		)
	}

	function renderEditIngredients() {
		const ingredients = recipe.ingredients;

		return (
			<textarea  
				className="form-control" 
				defaultValue={ingredients.join('\n')} 
				rows={Math.max(ingredients.length + 1, 12)} 
				onChange={() => setEditedRecipe({...recipe, 'ingredients':  event.target.value.split('\n')})}
			/>

		)
	}

	function renderViewInstructions() {
		const instructions = recipe.instructions;
		switch(instructions.type) {
			case 'one_step':
				return <p>{instructions.step} </p>
			
			case 'steps':
				return (
					<ol>
						{
							instructions.steps.map((step, index) => {
								return <li key={index}>{ step }</li>
							})
						}
					</ol>
				)
			
			case 'sections':
				return (
					<div>
					{
						instructions.sections.map((section) => {
							return (
								<div>
									<h6 className="initialism">
										{section.name} 
									</h6>
									<ol>
										{
											section.steps.map((step, index) => {
												return <li key={index}>{ step }</li>
											})
										}
									</ol>
								</div>
							)
						})
					}
					</div>
				)
		}
	}

	function renderEditInstructions() {
		const instructions = recipe.instructions;
		switch(instructions.type) {
			case 'one_step':
				return (
		    	<textarea 
		    		className="form-control" 
		    		name="instructions" 
		    		defaultValue={instructions.step}
		    		onChange={() => {
		    			setEditedRecipe({
		    				...recipe, 'instructions':  {type: 'one_step', step: event.target.value}
		    			})}
		    		}
		    	/>
				)
			
			case 'steps':
				return (
					<textarea 
						className="form-control" 
						name="instructions" 
						rows={Math.max(instructions.steps.length + 1, 12)} 
						defaultValue={instructions.steps.join('\n')}
						onChange={() => {
							setEditedRecipe({
								...recipe, 
								'instructions':  {
									type: 'steps', 
									steps: event.target.value.split('\n')
								}
							})}
						}
					/> 
				)
			
			case 'sections':
				return <div>Sorry, not implemented yet!</div>
				return (
					<div>
					{
						instructions.sections.map((section, sectionIndex) => {
							const tagName = `instructions-${sectionIndex}`
							return (
								<Fragment>
									<label for={tagName} className="initialism">{section.name}</label>			
									<textarea 
										className="form-control" 
										name={tagName} 
										rows={section.steps.length + 1 } 
										defaultValue={ section.steps.join('\n')}
										onChange={() => {
											console.log('todo')
										}}
									/>
								</Fragment>
							)
						})
					}
					</div>
				)
		}
	}

	function getTimeLabels(times) {
		return Object.entries(times).map(([key, seconds]) => {
	    return {
	    	label: `${key[0].toUpperCase() + key.slice(1)} Time`, 
	    	value: `${seconds / 60} minutes`
	    };
		})
	}


	function getKeywordCategoryValues() {
		let info = []
		recipe.category ? info.push({label: 'Category', value: recipe.category.join(', ')}) : null
		recipe.keywords ? info.push({label: 'Keywords', value: recipe.keywords.join(', ')}) : null
		return info
	}

	if (isLoading) {
		return (
			<div className="spinner-border text-danger" role="status">
		  	<span className="sr-only">Loading...</span>
		  </div>)
	}

	return (
		<div>
			<div className="row">
				<div className={recipe.image_url ? "col-sm-7" : "col-sm-12"}>
					<h1 className="display-4" style={{display: 'inline-block'}}>
						{recipe.name}
					</h1>
					<SubtitleBar recipe={recipe} />
					{
						recipe.description
							? <div id="description" className="collapse show">
				          <p className="font-italic">
				            "{recipe.description}""
				          </p>
				        </div>
				      : null
					}
				<InfoPanel info={
					[
						{label: 'Yield', value: recipe.yield},
					].concat(getTimeLabels(recipe.times))
				} />
				<div className="btn-group mb-3 mt-3">
					<input type="submit" value="Delete" className="btn btn-danger" onClick={handleDelete} />
				</div>
				</div>
				{recipe.image_url
					? <div className="col-sm-5">
							<img src={recipe.image_url} className="img-fluid rounded mx-auto d-block"/> 
						</div>
					: null
				}
			</div>
			<br/>
			<div className="row">
				<div className="col-sm-4">
					<ToggleableEditor 
						title={"Ingredients"}
						renderViewFunc={renderViewIngredients}
						renderEditFunc={renderEditIngredients}
						setEditSaved={setEditSaved}
						setEditedRecipe={setEditedRecipe}
					/>
				</div>
				<div className="col-sm-8">
					<ToggleableEditor 
						title={"Instructions"}
						renderViewFunc={renderViewInstructions}
						renderEditFunc={renderEditInstructions} 
						setEditSaved={setEditSaved}
						setEditedRecipe={setEditedRecipe} // remove
					/>
				</div>
			</div>
			<div className="row m-3">
				<InfoPanel info={getKeywordCategoryValues()} />
			</div>
		</div>
	)
}

export default RecipeView