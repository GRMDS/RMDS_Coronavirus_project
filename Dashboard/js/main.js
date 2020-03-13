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


    function popUpEvent(target) {
        
        let query = target.graphic.layer.createQuery();
        query.where = "__OBJECTID = " + target.graphic.attributes["__OBJECTID"];
        query.outFields = ["*"];

        queryNewsCount = 0;
        
        return target.graphic.layer.queryFeatures(query).then(function(result) {
            let info = result.features[0].attributes;
            if (queryNewsCount === 0) {
                queryNews(info["Country/Region"], info["Province/State"]);
            }
            queryNewsCount++;
            
            getProvince(info["Country/Region"], info["Province/State"], info["Latitude"], info["Longitude"]);
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

function readCSVFile() {
    Papa.parse("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv", {
        download: true,
	    complete: function(results) {
            cData = results;
	    }
    });

    Papa.parse("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv", {
        download: true,
        complete: function(results) {
            dData = results;
        }
    });

    Papa.parse("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv", {
        download: true,
        complete: function(results) {
            rData = results;
        }
    });
}

// 确保每次只查询一次新闻
let queryNewsCount = 0;

let cData = {};
let rData = {};
let dData = {};

// init();
readCSVFile();


let getProvince = function(country, province) {
    // console.log("Country = " + country + ", Province = " + province);
    
    let dataIndex = queryProvince(country, province);
    
    // console.log(cData.data[dataIndex]);
    if (dataIndex == -1) {
        return;
    }

    let data = cData.data[dataIndex];
    let rdata = rData.data[dataIndex];
    let ddata = dData.data[dataIndex];

    let dateArray = [];
    let dataArray = [];
    let deathArray = [];
    let recoveredArray = [];
    for (let i = 4; i < cData.data[0].length; i++) {
        dateArray.push(cData.data[0][i]);
        dataArray.push(data[i]);
        deathArray.push(ddata[i]);
        recoveredArray.push(rdata[i]);
    }
    let chartDiv = document.getElementById("chart-2");
    if (chartDiv === null) {
        console.log("Can't find the chart div.");
        return;
    }
    let title = "";
    if (data[0] === "") {
        title = "Country: " + data[1];
    }
    else {
        title = "Province / State: " + data[0];
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
            data: dateArray,
        },
        yAxis: {

        },
        series: [{
            name: 'Confirmed',
            type: 'line',
            data: dataArray,
        },
        {
            name: 'Recovered',
            type: 'line',
            data: recoveredArray,
        },
        {
            name: 'Deaths',
            type: 'line',
            data: deathArray,
        }]
    }

    // 使用刚指定的配置项和数据显示图表。
    myChart.setOption(options);



};

function compareCountry(target, source) {
    if (target === null || target === "") {
        return false;
    }
    if (source === null || source === "") {
        return false;
    }
    const targetList = target.split(' ');
    const sourceList = source.split(' ');
    if (sourceList.length === 1 && targetList.length === 1) {
        if (targetList[0].indexOf(sourceList[0]) !== -1) {
            return true;
        }
    }
    else {
        if (target.indexOf(source) !== -1) {
            return true;
        }
    }
    
    return false;
}

function compareProvince(target, source) {
    if (target === null || target === "") {
        return false;
    }
    if (source === null || source === "") {
        return false;
    }
    const sourceList = source.split(' ');
    for (let i = 0; i < sourceList.length; i++) {
        let index = 0;
        index = target.toLowerCase().indexOf(sourceList[i].toLowerCase());
        if (index !== -1 && index === 0) {
            return true;
        }
    }

    return false;
}


function queryProvince(country, province) {
    if (isEmpty(cData)) {
        return -1;
    }
    
    if (province === '') {
        for (let i = 1; i < cData.data.length; i++) {
            if (compareCountry(cData.data[i][1], country) == true) {
                return i;
            } 
        }
    }
    else {
        for (let i = 1; i < cData.data.length; i++) {
            if (cData.data[i][0] !== "") {
                if (compareProvince(cData.data[i][0], province) == true) {
                    if (compareCountry(cData.data[i][1], country) == true) {
                        return i;
                    }
                    // return i;
                }
            }
            else {
                if (compareCountry(cData.data[i][1], country) == true) {
                    return i;
                }
            }
        }
    }
    return 13;
}



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
    if (arcDiv === null || arcDiv === 'undefined') {
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

queryNews("Mainland China", "Wuhan");
getProvince("Mainland China", "Hubei");



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

