async function getData(url) {
  const response = await fetch(url);
  return await response.json();
}

async function postData(url = '', data = {}) {
  // Default options are marked with *
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });
  return await response.json();
}

function AddRecipeBox(props) {
  return (
    <form method="post" className="needs-validation mb-3">
        <div className="form-group">
            <input type="url" className="form-control form-control-lg" placeholder="Enter link to recipe" name="url" required></input>
        </div>
        <button type="submit" onClick={props.addRecipe} className="btn btn-primary">Add</button>
    </form>
  )
}


function RecipeCard(props) {
    const recipe = props.recipe;
    return (
        <div className="card shadow-sm">
        {recipe.image_url ? <img className="card-img-top" src={recipe.image_url} alt="Recipe image"></img>: null}
        <div className="card-body">
            <h5 className="card-title"><span className="recipe-name">{recipe.name}</span> <span className="text-secondary small recipe-domain">({recipe.domain})</span></h5>
            <p className="card-text font-italic small">{recipe.description && recipe.description.length > 150 ? recipe.description.slice(0, 150).trim() + "..." : recipe.description}</p>
            <a href={recipe.id + "/view"} className="btn btn-primary stretched-link" >View</a>
            </div>
        </div>
        );
}

function RecipeCardColumns(props) {
  const recipeCards = props.recipes.map((recipe) => 
    <RecipeCard key={recipe.id} recipe={recipe}/>
  );
  return <div id="recipe-cards" className="card-columns">
  {recipeCards}
  </div>
}

function SearchBox(props) {
  return (
    <div className="input-group mb-3">
      <input className="form-control" id="filterByName" type="text" placeholder="Filter by name" 
      value={props.nameFilterText} onChange={props.handleNameFilterChange}></input>
      <input className="form-control" id="filterByDomain" type="text" 
      placeholder="Filter by site"  value={props.siteFilterText}
      onChange={props.handleSiteFilterChange}></input>
      <button className="btn btn-outline-danger ml-1" id="resetFilters" onClick={props.handleFilterReset}>Reset</button>
    </div>
    )
}

class RecipeTable extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
           recipes: [],
           nameFilterText: '',
           siteFilterText: ''
        };
        this.getRecipes = this.getRecipes.bind(this);
        this.handleNameFilterChange = this.handleNameFilterChange.bind(this);
        this.handleSiteFilterChange = this.handleSiteFilterChange.bind(this);
        this.handleFilterReset = this.handleFilterReset.bind(this);
        this.handleSubmitRecipe = this.handleSubmitRecipe.bind(this);
    }

    handleNameFilterChange(event) {
      this.setState({nameFilterText: event.target.value});
    }

    handleSiteFilterChange(event) {
      this.setState({siteFilterText: event.target.value});
    }

    handleFilterReset(event) {
      this.setState({siteFilterText: '', nameFilterText: ''});
    }

    handleSubmitRecipe(event) {
      let url = event.target.value;
      console.log(url)
      postData('/api/recipes/add', {url: url})
        .then((recipe) => {
          this.setState({
            recipes: [recipe].concat(recipes)
          });
        });
    }

    getRecipes() {
      getData("/api/recipes")
        .then((data) => {
          data.forEach(recipe => {recipe.domain = new URL(recipe.url).hostname})
          this.setState({
            recipes: data
          });
        });
    }
    
    componentDidMount() {
      this.getRecipes();
    }
    
    render() {
      let recipes = this.state.recipes;
      const nameFilterText = this.state.nameFilterText
      if (nameFilterText) {
        recipes = recipes.filter(recipe => recipe.name.toLowerCase().search(nameFilterText.toLowerCase()) > -1);
      }
      const siteFilterText = this.state.siteFilterText
      if (siteFilterText) {
        recipes = recipes.filter(recipe => recipe.domain.search(siteFilterText.toLowerCase()) > -1);
      }

      return (
        <div>
            <AddRecipeBox handleSubmitRecipe={this.state.handleSubmitRecipe} />
            <SearchBox nameFilterText={this.state.nameFilterText} 
            siteFilterText={this.state.siteFilterText}
            handleNameFilterChange={this.handleNameFilterChange} 
            handleSiteFilterChange={this.handleSiteFilterChange}
            handleFilterReset={this.handleFilterReset}
            />
            <RecipeCardColumns recipes={recipes} />
        </div>
      )
    }
}

ReactDOM.render(
    <RecipeTable />,
    document.getElementById('react-recipe-container')
  );