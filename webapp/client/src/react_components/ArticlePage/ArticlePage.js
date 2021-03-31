
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
		query += "&mode=exact";

		console.log(query);
		const response = await fetch(query);
		const jsonData = await response.json();
        setIsLoaded(true);
		console.log(jsonData);
		setResultData(jsonData);
		console.log(jsonData[0]['pdf_url']);
		setPdfUrl(jsonData[0]['pdf_url']);

	};
	if(pdfUrl){
		return(

			
			<div class="pdfview" >
			<PDFViewer document={{url:pdfUrl}}/>
			</div>
			
		)
	}else{
		return null
	}

}
export default ArticlePage;
