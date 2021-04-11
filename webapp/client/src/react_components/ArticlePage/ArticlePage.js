import "./styles.css";
import { withRouter, useParams, useHistory } from "react-router-dom";
import { PDFReader } from 'reactjs-pdf-reader';
import React, { useState, useEffect } from 'react';
import { Document } from 'react-pdf';
import PDFViewer from 'pdf-viewer-reactjs'
import CanvasJS from 'canvasjs';

function ArticlePage(props){
  const history=useHistory();
  let { id }= useParams();
  const [relatedData, setRelatedData] = useState();
  const [articleData, setArticleData] = useState();
  const [pdfUrl, setPdfUrl] = useState();
  const getFetch = async () => {

    let query = "http://localhost:5000/search?id=";
    query += id;
    query += "&mode=related";

    let response = await fetch(query);
    let jsonData = await response.json();
    setRelatedData(jsonData);

    query = "http://localhost:5000/search?id=";
    query += id;
    query += "&mode=exact";
    response = await fetch(query);
    jsonData = await response.json();
    setPdfUrl("http://localhost:5000/article/pdf_by_path/" + jsonData[0]["pdf"])

  };
  const goToArticle=(article)=>{
    article=JSON.stringify(article);
    article=article.substring(1, article.length-1)
    history.push("/article/"+article);
  };
  useEffect(() => {
    getFetch();
  }, [id]);
  if (pdfUrl) {
    return(
      <div>
        <div className="pdfview">
          <PDFViewer document={{url:pdfUrl}}/>
        </div>
        <h2>Related Papers:</h2>
        <div>
          <ol>
          {
            relatedData && relatedData.length>0 && relatedData?.map(article => {
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
  } else {
    return null
  }
}

export default ArticlePage;
