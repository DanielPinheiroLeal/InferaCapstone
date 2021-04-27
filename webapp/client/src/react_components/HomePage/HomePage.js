import React from 'react';
import "./styles.css";
import { withRouter, useHistory } from "react-router-dom";
import SearchBar from '../SearchBar/SearchBar.js';

function HomePage (props){




	return (
    <div className="searchContainer">
        <h2 id="searchHeader">Start Search</h2>
        <br></br>
        <SearchBar prop={this}/>
        


        
    </div>
	)


}
export default HomePage;
