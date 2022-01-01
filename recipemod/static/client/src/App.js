import React from "react";
import {
	BrowserRouter as Router, Switch, Route, Link, useParams
} from "react-router-dom";
import RecipeList from "./RecipeList.js";
import RecipeView from "./RecipeView.js";

export default function App() {
	return (
		<Router>
			<Switch>
				<Route path='/recipe/:recipeId/' children={<Recipe/>} />
				<Route path="/">
					<RecipeList/>
				</Route>
			</Switch>
		</Router>
	)
}

function Recipe() {
	let { recipeId } = useParams();
	return (
		<RecipeView recipeId={recipeId} />
	)
}