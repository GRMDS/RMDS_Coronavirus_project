require([
    "esri/Map",
    "esri/views/MapView",
    "esri/layers/CSVLayer",
], function(Map, 
            MapView, 
            CSVLayer,
            ) 
{
    var map = new Map({
        basemap: "topo-vector"
    });

    var view = new MapView({
        container: "chart-1",
        map: map,
        center: [121.4800, 31.2200], // longitude, latitude
        zoom: 5
    });
    
    var popupProvince = {
        "title": "Cases",
        "content": popUpEvent
    };

    // Response for 
    function popUpEvent(target) {
        
        let query = target.graphic.layer.createQuery();
        if (query === null) {
            return;
        }
        query.where = "__OBJECTID = " + target.graphic.attributes["__OBJECTID"];
        query.outFields = ["*"];

        queryNewsCount = 0;
        
        return target.graphic.layer.queryFeatures(query).then(function(result) {
            let info = result.features[0].attributes;
            if (queryNewsCount === 0) {
                queryNews(info["Country/Region"], info["Province/State"]);
            }
            queryNewsCount++;
            
            // Query Data from the remote Data Server
            queryNode(info["Country/Region"], info["Province/State"]);
            return ("<b>Country: </b>" + info["Country/Region"] + "<br>"
                    + "<b>City / States: </b>" + info["Province/State"] + "<br>"
                    //+ "<b>Latitude: </b>" + info["Latitude"] + "<br>"
                    //+ "<b>Longitude: </b>" + info["Longitude"] + "<br>"
                    + "<b>Confirmed: </b>" + info["Confirmed"] + "<br>"
                    + "<b>Recovered: </b>" + info["Recovered"] + "<br>"
                    + "<b>Deaths: </b>" + info["Deaths"] + "<br>");
        });
    }

    var JHULayer = new CSVLayer({
        url: "https://grmdsrecommendation.s3-us-west-1.amazonaws.com/integrated.csv",
        opacity: 0.6,
        popupTemplate: popupProvince,

    });

    JHULayer.renderer = {
        type: "simple",
        symbol: {
            type: "simple-marker",
            color: "red",
            outline: null
        },
        visualVariables: [{
            type: "size",
            field: "Confirmed",
            minDataValue: 0,
            maxDataValue: 3000,
            minSize: 8,
            maxSize: 80
        }],
    };

    map.add(JHULayer);
});

function isEmpty(obj) {
    for(var prop in obj) {
        if(obj.hasOwnProperty(prop)) {
            return false;
        }
    }
    return true;
}

// 确保每次只查询一次新闻
let queryNewsCount = 0;

function updateChart(data) {
    let chartDiv = document.getElementById("chart-2");
    if (chartDiv === null) {
        console.log("Can't find the chart div.");
        return;
    }
    let title = "";
    if (data.province === "") {
        title = "Country: " + data.country;
    }
    else {
        title = "Province: " + data.province;
    }
    // 基于已有的Div，初始化echarts实例
    echarts.dispose(chartDiv);

    let myChart = echarts.init(chartDiv);
    // 指定图表的配置项和数据
    let options = {
        title: {
            // text: ,
            text: title,
        },
        tooltip: {
            trigger: 'axis'
        },
        legend: {
            data: ['Confirmed', 'Recovered', 'Deaths'],
        },
        xAxis: {
            data: data.date,
        },
        yAxis: {

        },
        series: [{
            name: 'Confirmed',
            type: 'line',
            data: data.confirmed,
        },
        {
            name: 'Recovered',
            type: 'line',
            data: data.recovered,
        },
        {
            name: 'Deaths',
            type: 'line',
            data: data.deaths,
        }]
    }

    // 使用刚指定的配置项和数据显示图表。
    myChart.setOption(options);
}

// Google News RSS parser
function parseXML(xmlNode) {
    if (xmlNode === null) {
        console.log("XML is empty");
    }
    let parser = new DOMParser();
    let xmlDoc = parser.parseFromString(xmlNode, "text/xml");
    let itemNode = xmlDoc.getElementsByTagName("item");
    if (itemNode === null && itemNode.length == 0) {
        console.log("Can not find the Item Element");
    }
    const MAX_NODES = 10;

    let arcDiv = document.getElementById("viewRightDiv");
    if (arcDiv === null || typeof arcDiv === 'undefined') {
        console.log("Can't get the news bar");
        return;
    }
    arcDiv.innerHTML = '';

    for (let i = 0; i < itemNode.length && i < MAX_NODES; i++) {
        let titleNode = itemNode[i].getElementsByTagName("title");
        if (titleNode === null || titleNode.length === 0) {
            console.log("News title is not existed.");
            break;
        }
        let linkNode = itemNode[i].getElementsByTagName("link");
        if (linkNode === null || linkNode.length === 0) {
            console.log("News link is not existed.");
            break;
        }
        let pubDateNode = itemNode[i].getElementsByTagName("pubDate");
        if (pubDateNode === null || pubDateNode.length === 0) {
            console.log("News pubDate is not existed.");
            break;
        }

        let title = titleNode[0].innerHTML;
        let link = linkNode[0].innerHTML;
        let pubDate = pubDateNode[0].innerHTML;

        let newsNode = {
            title: title,
            link: link,
            pubDate: pubDate,
        };

        addNews(newsNode);
    }
}

function addNews(newsNode) {
    let arcDiv = document.getElementById("viewRightDiv");
    if (arcDiv === null || arcDiv === 'undefined') {
        console.log("Can't get the news bar");
        return;
    }
    
    let newsDiv = document.createElement("div");
    newsDiv.classList.add("newsNode");

    let newsTitle = document.createElement("div");
    newsTitle.classList.add("newsNodeTitle");
    newsTitle.innerHTML = newsNode.title;
    newsDiv.appendChild(newsTitle);

    let newsLink = document.createElement("a");
    newsLink.classList.add("newsNodeLink");
    newsLink.href = newsNode.link;
    newsLink.innerHTML = newsNode.title;
    newsLink.setAttribute("target", "_blank");
    newsDiv.appendChild(newsLink);

    let newsPubDate = document.createElement("div");
    newsPubDate.classList.add("newsNodePubDate");
    newsPubDate.innerHTML = newsNode.pubDate;
    newsDiv.appendChild(newsPubDate);

    arcDiv.appendChild(newsDiv);
}


function queryNews(country, province) {
    let queryLocation = ""
    if (province !== 'undefined' && province !== null && province.length !== 0) {
        queryLocation = "+" + province
    }
    else {
        if (country !== 'undefined' && country !== null && country.length !== 0) {
            queryLocation = "+" + country;
        }
    }
    
    let baseUrlStart = "https://news.google.com/rss/search?q=coronavirus"
    let baseUrlEnd = "&hl=en-US&gl=US&ceid=US:en"

    let baseUrl = baseUrlStart + queryLocation + baseUrlEnd;
    const proxyUrl = "https://morning-ridge-54662.herokuapp.com/";

    console.log(baseUrl);

    fetch(proxyUrl + baseUrl) // https://cors-anywhere.herokuapp.com/https://example.com
        .then(response => response.text())
        .then((contents) => {parseXML(contents)})
        .catch(() => console.log("Can’t access " + baseUrl + " response. Blocked by browser?"))
}

function queryNode(country, province) {
    if (typeof country === 'undefined' || typeof province === 'undefined') {
        return;
    }

    let baseUrl = "https://36techfreedom.com:5000/data";
    let data = {country: country, province: province};
    postData(baseUrl, data)
        .then((data) => {
            console.log(data);
            updateChart(data);
        }) // JSON from `response.json()` call
        .catch(error => console.error(error))
    
}

function postData(url, data) {
    // Default options are marked with *
    return fetch(url, {
        body: JSON.stringify(data), // must match 'Content-Type' header
        //cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
        //credentials: 'include', // include, same-origin, *omit
        headers: {
            'content-type': 'application/json'
        },
        method: 'POST', // *GET, POST, PUT, DELETE, etc.
        mode: 'cors', // no-cors, cors, *same-origin
        //redirect: 'follow', // manual, *follow, error
        //referrer: 'no-referrer', // *client, no-referrer
    })
    .then(response => response.json()) // parses response to JSON
}

(function($) { // Begin jQuery
    $(function() { // DOM ready
      // If a link has a dropdown, add sub menu toggle.
      $('nav ul li a:not(:only-child)').click(function(e) {
        $(this).siblings('.nav-dropdown').toggle();
        // Close one dropdown when selecting another
        $('.nav-dropdown').not($(this).siblings()).hide();
        e.stopPropagation();
      });
      // Clicking away from dropdown will remove the dropdown class
      $('html').click(function() {
        $('.nav-dropdown').hide();
      });
      // Toggle open and close nav styles on click
      $('#nav-toggle').click(function() {
        $('nav ul').slideToggle();
      });
      // Hamburger to X toggle
      $('#nav-toggle').on('click', function() {
        this.classList.toggle('active');
      });
    }); // end DOM ready
})(jQuery); // end jQuery

