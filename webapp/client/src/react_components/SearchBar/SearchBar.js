
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
