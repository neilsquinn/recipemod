import React from "react";

function SearchBox(props) {
  return (
    <div className="input-group mb-3">
      <input className="form-control" id="filterByName" type="search" placeholder="Filter by name" 
      value={props.nameFilterText} onChange={props.handleNameFilterChange}></input>
      <input className="form-control" id="filterByDomain" type="search" 
      placeholder="Filter by site"  value={props.siteFilterText}
      onChange={props.handleSiteFilterChange}></input>
      <button className="btn btn-outline-danger ml-1" id="resetFilters" onClick={props.handleFilterReset}>Reset</button>
    </div>
    )
}

export default SearchBox;