import React from 'react';
import "./styles.css";
import { withRouter, useHistory } from "react-router-dom";
import SearchBar from '../SearchBar/SearchBar.js';
import { TagCloud } from 'react-tagcloud';
import { useState, useEffect } from 'react';
function HomePage (props){
	// constructor(props) {
  //   super(props);
  //   this.state = {
  //     value: ''
  //   };

  //   this.handleChange = this.handleChange.bind(this);
  //   this.handleSubmit = this.handleSubmit.bind(this);
  // }
	
	// handleChange(event) {
  //   		this.setState({value: event.target.value});
  // 	}

	// handleSubmit(event) {
  //   event.preventDefault();
  //   let no_spaces=this.state.value.replace(/\s/g,'')
  //   if (no_spaces === "") {
  //     event.preventDefault();
  //     alert("Please enter a valid search query.");
  //     return;
  //   }
  //   console.log("submit")
  //   console.log(this.state.value);
  //   this.props.history.push(`/search/${this.state.value}`);
  //   //this.props.showMarker(this.state.value)
	// }
  const getFetch = async () => {

    let query = "http://localhost:5000/topicwords/-1";
    //query += "&mode=exact";
    let response = await fetch(query);
    let jsonData = await response.json();
    console.log(jsonData)
  }
  useEffect(() => {
    getFetch();
  }, []);
	return (
    <div className="searchContainer">
        <h2 id="searchHeader">Start Search</h2>
        <br></br>
        <SearchBar prop={this}/>
        
    </div>
	)

}
export default HomePage;
