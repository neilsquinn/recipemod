import React, {useState, useEffect} from 'react';
import axios from 'axios';
import {useHistory} from "react-router-dom";

import SubtitleBar from './components/SubtitleBar.js';
import InfoPanel from './components/InfoPanel.js';

// TODO add onError for image- onError={(e) => e.target.src = some url} works if i have a placeholder 

function RecipeView(props) {

	const [recipe, setRecipe] = useState({});
	const [isLoading, setIsLoading] = useState(true);
	let history = useHistory();

	useEffect(() => {
		setIsLoading(true);
		axios.get(`/api/recipes/${props.recipeId}`)
			.then(resp => {
				setRecipe(resp.data);
				setIsLoading(false);
			});
	}, []);
	// console.log(recipe);

	function handleDelete(event) {
		if (!confirm('Are you sure?')) {
			return null;
		}
		axios.delete(`/api/recipes/${props.recipeId}`)
			.then(resp => history.push("/"))
			.catch(error => alert('Unable to delete recipe!'));
		
	}

	function renderInstructions() {
		switch(recipe.instructions.type) {
			case 'one_step':
				return <p>{recipe.instructions.step} </p>
			
			case 'steps':
				return (
					<ol>
						{
							recipe.instructions.steps.map((step, index) => {
								return <li key={index}>{ step }</li>
							})
						}
					</ol>
				)
			
			case 'sections':
				return (
					<div>
					{
						recipe.instructions.sections.map((section) => {
							console.log(section.name)
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

	function getTimeLabels(times) {
		return Object.entries(times).map(([key, seconds]) => {
	    return {
	    	label: `${key[0].toUpperCase() + key.slice(1)} Time`, 
	    	value: `${seconds / 60} minutes`
	    };
		})
	}

	function getKeywordCategoryValues () {
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
					<h1 className="display-4">
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
					<h3>
						Ingredients 
					</h3>
					<ul>
						{recipe.ingredients.map((ingredient, index) => <li key={index}>{ingredient}</li>)}
					</ul>
				</div>
				<div className="col-sm-8">
					<h3>
						Instructions 
					</h3>
					{renderInstructions()}
				</div>
			</div>
			<div className="row m-3">
				<InfoPanel info={getKeywordCategoryValues()} />
			</div>
		</div>
	)
}

export default RecipeView