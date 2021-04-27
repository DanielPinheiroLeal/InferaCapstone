
import "./styles.css";
import { withRouter, useParams, useHistory } from "react-router-dom";
import React, { useState, useEffect } from 'react';
import { TagCloud } from 'react-tagcloud';

function SearchPage(props){
	const history=useHistory();
    const [resultData, setResultData] = useState();
    const [field, setField] = useState();
	const [type, setType] = useState();

	const [topicData, setTopicData] = useState();
	
	const getFetch = async () => {
  
	  let query = "http://localhost:5000/topicwords/-1";
	  //query += "&mode=exact";
	  let response = await fetch(query);
	  let jsonData = await response.json();
	  console.log(jsonData)
	  let td = []
	  let uni = []
	  for (let i in jsonData){
		for (let j in jsonData[i]){
		  if(uni.includes(jsonData[i][j])==false){
		  	td.push({value: jsonData[i][j]})
			uni.push(jsonData[i][j])
		  }
		}
	  }
	  setTopicData(td)
	}
	const addTerm=(term)=>{
	  //article=JSON.stringify(article);
	  //article=article.substring(1, article.length-1)
	  if(field){
	  	setField(field+" "+term)
	  }else{
		setField(term)
	  }

	};
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
	useEffect(() => {
		getFetch();
	}, []);
	if(topicData){
		return(
			<div>
			
				<form onSubmit={handleSubmit}>
					<input type="text" value={field} onChange={handleChange}/>

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
					<TagCloud
				minSize={12}
				maxSize={35}
				tags={topicData}
				onClick={tag=>addTerm(tag.value)}
				/>

			</div>


				
		)
	}else{
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

}
export default SearchPage;
