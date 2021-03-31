
import "./styles.css";
import { withRouter, useParams, useHistory } from "react-router-dom";
import { PDFReader } from 'reactjs-pdf-reader';
import React, { useState, useEffect } from 'react';
import { Document } from 'react-pdf';
import PDFViewer from 'pdf-viewer-reactjs'

function ArticlePage(props){
	const history=useHistory();
    let { id }= useParams();
    const [resultData, setResultData] = useState();
    const [isLoaded, setIsLoaded] = useState();
	const [pdfUrl, setPdfUrl] = useState();
	useEffect(() => {
    	getFetch();
  	}, []);
	const getFetch = async () => {

        let query = "http://localhost:5000/search?title=";
		//id=id.substring(1, id.length-1)
		query += id;
		query += "&mode=related";

		console.log(query);
		const response = await fetch(query);
		const jsonData = await response.json();
        setIsLoaded(true);
		console.log(jsonData);
		setResultData(jsonData);
		console.log(jsonData[0]['pdf_url']);
		setPdfUrl(jsonData[0]['pdf_url']);

	};
	const goToArticle=(article)=>{
		article=JSON.stringify(article);
		article=article.substring(1, article.length-1)
		history.push("/article/"+article);
	};
	if(pdfUrl){
		return(

			<div>
				<div>
			<div class="pdfview" >
			<PDFViewer document={{url:pdfUrl}}/>
			</div>
			</div>
			<h2>Related Papers:</h2>
			 <div>
			 <ol>
			 {
				 resultData && resultData.length>0 && resultData?.map(article => {
					 return <li key={article.id} align="start" onClick={()=>goToArticle(article.title)}>
						 <div>
							 <p>{article.title}</p>
							 <p>{article.author}</p>
						 </div>
					 </li>
				 })
			 }
			 </ol>
		 </div>
		 </div>
			
		)
	}else{
		return null
	}

}
export default ArticlePage;
