import "./styles.css";
import { withRouter, useParams, useHistory } from "react-router-dom";
import { PDFReader } from 'reactjs-pdf-reader';
import React, { useState, useEffect } from 'react';
import { Document } from 'react-pdf';
import PDFViewer from 'pdf-viewer-reactjs'
import CanvasJSReact from "../../canvasjs/canvasjs.react.js"
var CanvasJS = CanvasJSReact.CanvasJS;
var CanvasJSChart = CanvasJSReact.CanvasJSChart;

function ArticlePage(props){
  const history=useHistory();
  let { id }= useParams();
  const [relatedData, setRelatedData] = useState();
  const [articleData, setArticleData] = useState();
  const [pdfUrl, setPdfUrl] = useState();
  const [dataPoints, setDataPoints] = useState();
  const getFetch = async () => {

    // let query = "http://localhost:5000/search?id=";
    // query += id;
    // query += "&mode=related";

    // let response = await fetch(query);
    // let jsonData = await response.json();
    // setRelatedData(jsonData);

    let query = "http://localhost:5000/visualization/";
    query += id;
    //query += "&mode=exact";
    let response = await fetch(query);
    let jsonData = await response.json();
    console.log(jsonData)
    let data=[]
    for (let i in jsonData){
      let entry = {}
      entry.x=jsonData[i]['processed_coord'][0]
      entry.y=jsonData[i]['processed_coord'][1]
      entry.name=jsonData[i]['title']
      data.push(entry)

    }
    //setDataPoints(data)
    console.log(data)
    setDataPoints({
      theme: "dark2",
			animationEnabled: true,
			zoomEnabled: true,
			title:{
				text: ""
			},
			axisX: {
				//title:"Temperature (in °C)",
				//suffix: "°C",
        gridThickness: 1,
				crosshair: {
					enabled: true,
					snapToDataPoint: true
				}
			},
			axisY:{
				//title: "Sales",
				crosshair: {
					enabled: true,
					snapToDataPoint: true
				}
			},
			data:[{
				type: "scatter",
				markerSize: 15,
				toolTipContent: "{name}: {x}, {y}",
				dataPoints: data
			}]
    })
    setRelatedData(jsonData.slice(1))
    setPdfUrl(jsonData[0]["pdf_url"])


  };
  const goToArticle=(article)=>{
    //article=JSON.stringify(article);
    //article=article.substring(1, article.length-1)
    history.push("/article/"+article);
  };
  useEffect(() => {
    getFetch();
  }, [id]);
  if (pdfUrl) {
    return(
      <div>
        <div className="pdfview">
          <PDFViewer document={{url:encodeURI(pdfUrl)}}/>
        </div>
        <div>
        <CanvasJSChart options = {dataPoints} 
            /* onRef = {ref => this.chart = ref} */
        />
      </div>
        <h2>Related Papers:</h2>
        <div>
          <ol>
          {
            relatedData && relatedData.length>0 && relatedData?.map(article => {
              return <li key={article.id} align="start" onClick={()=>goToArticle(article.paper_id)}>
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
