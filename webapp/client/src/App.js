import React from 'react';

import { Route, Switch, withRouter, Link, useHistory } from "react-router-dom";
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import Navbar from 'react-bootstrap/Navbar';
import Nav from 'react-bootstrap/Nav';
import NavDropdown from 'react-bootstrap/NavDropdown';

import HomePage from './react_components/HomePage/HomePage.js';
import ResultPage from './react_components/ResultPage/ResultPage.js';
import ArticlePage from './react_components/ArticlePage/ArticlePage.js';


function App() {
const history=useHistory
  return (
    <div className="App">
	  <Navbar bg="dark">
	  	<Navbar.Brand href="#home">Document Explorer</Navbar.Brand>
	 	<Navbar.Toggle/>
		<Navbar.Collapse className="justify-content-end">
		</Navbar.Collapse>
	</Navbar>
	
	<Switch>
		<Route exact path="/" render ={()=>
			<div className="homePage">
				<HomePage app={this}/>
			</div>
		}/>
	  	<Route exact path="/search/:id" render ={()=>
			<div className="searchPage">
				<ResultPage app={this}/>
			</div>
		}/>
	  	<Route exact path="/article/:id" render ={()=>
			<div className="articlePage">
				<ArticlePage app={this}/>
			</div>
		}/>

	</Switch>
    </div>);
  
}

export default withRouter(App);
