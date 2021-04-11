import "./styles.css";
import { withRouter, useParams, useHistory } from "react-router-dom";
import React, { useState, useEffect } from 'react';

function SearchPage(props){

	const history=useHistory();
    const [resultData, setResultData] = useState();
    const [field, setField] = useState();
	const [type, setType] = useState();
	//setType("title")
	const handleSubmit=(e)=>{
		e.preventDefault()
		if(!type){
			alert("Please select a search type")
			return
		}
		//console.log(e.target.value)
		setField(e.target.value)
		let query="/search/search?"+type+"="+field
		console.log(query)
		console.log("TIME: ")
		var date = new Date().getDate(); //To get the Current Date
		var month = new Date().getMonth() + 1; //To get the Current Month
		var year = new Date().getFullYear(); //To get the Current Year
		var hours = new Date().getHours(); //To get the Current Hours
		var min = new Date().getMinutes(); //To get the Current Minutes
		var sec = new Date().getSeconds(); //To get the Current Seconds
		var msec = new Date().getMilliseconds(); //To get the Current Seconds
		console.log(hours)
		console.log(min)
		console.log(sec)
		console.log(msec)
		history.push(query)
	}
	let handleChange=(e)=>{
		e.preventDefault()
		console.log(e.target.value)
		setField(e.target.value)
		console.log(type)
		//history.push
	}
	
	return(
		<div>
			<form onSubmit={handleSubmit}>
				<input type="text" onChange={handleChange}/>

				<input type="submit" value="Submit" />
				<br/>
				<div >
					<input type="radio"  value="title" checked={type==="title"} onChange={()=>setType("title")}/>
					<label for="title">Title</label>
					<input type="radio"  value="author" checked={type==="author"} onChange={()=>setType("author")}/>
					<label for="author">Author</label>
					<input type="radio" value="topic" checked={type==="topic"} onChange={()=>setType("topic")}/>
					<label for="topic">Topic</label>
				</div>


			</form>

		</div>


			
	)


}

export default SearchPage;
