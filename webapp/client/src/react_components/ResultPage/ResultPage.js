import React, { useState, useEffect } from 'react';
import "./styles.css";
import { withRouter, useLocation, useHistory } from "react-router-dom";
import SearchBar from '../SearchBar/SearchBar.js';

function ResultPage(props){
  const getFetch = async () => {
    console.log(title);
    console.log(author);
    console.log(topicString);

    let query = 'http://localhost:5000/search?';
    if (title) {
      query += 'title=';
      query += title;
      query += '&mode=exact';
    } else if (author) {
      query += 'author=';
      query += author;
      query += '&mode=exact';
    } else if (topicString) {
      query += 'topic=';
      query += topicString;
    }
    console.log(query);
    const response = await fetch(query);
    const jsonData = await response.json();
    setIsLoaded(true);
    console.log(jsonData);
    setResultData(jsonData);
  };
  const history=useHistory();
  let location=useLocation();
  console.log(location);
  const search = location.search;
  const title = new URLSearchParams(search).get('title');
  const author = new URLSearchParams(search).get('author');
  const topicString = new URLSearchParams(search).get('topic');
  const [resultData, setResultData] = useState();
  const [isLoaded, setIsLoaded] = useState();

  useEffect(() => {
    getFetch();
  }, [search]);

  const goToArticle=(article)=>{
    article=JSON.stringify(article);
    article=article.substring(1, article.length-1)
    history.push("/article/"+article);
  };

  if(resultData && resultData.length>0 && Array.isArray(resultData)){
    return (
      <div>
        <div className="searchContainer">
          <h2 id="searchHeader">Results</h2>
          <br></br>
          <SearchBar history={history}/>
        </div>
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
  } else {
    return (
      <div>
        <div className="searchContainer">
          <h2 id="searchHeader">Results</h2>
          <p>{location.pathname}</p>
          <p>{location.search}</p>
          <br></br>
          <SearchBar history={history}/>
        </div>
        <div>
          No Results Found
        </div>
      </div>
    )
  }
}

export default withRouter(ResultPage);
