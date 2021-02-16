import React from 'react';
import "./styles.css";
import { withRouter } from "react-router-dom";

class HomePage extends React.Component{
	constructor(props) {
    super(props);
    this.state = {
      value: ''
    };

    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }
	
	handleChange(event) {
    		this.setState({value: event.target.value});
  	}

	handleSubmit(event) {
	let no_spaces=this.state.value.replace(/\s/g,'')
	if (no_spaces === "") {
		event.preventDefault();
		alert("Please enter a valid search query.");
		return;
	}
	this.props.history.push(`/search/${this.state.value}`);
	this.props.showMarker(this.state.value)
	}
	
	render() {return (
        <div className="searchFormContainer">
            <h2 id="searchHeader">Start Search</h2>
            <br></br>
            <form onSubmit={this.handleSubmit}>
	        <label></label>
                <input type="text" value={this.state.value} onChange={this.handleChange}/>
                <br></br>
                <br></br>
                <br></br>
                <input class="searchButtonFormPage" type="submit" value="Submit" />
            </form>
        </div>
	)}

}
export default HomePage;
