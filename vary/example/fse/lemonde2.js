if(document.getElementById("articleBody") != null){
    var urlMod = window.location.href.replace("www.fakenewspaperpl.com","subscribers.fakenewspaperpl.com");
    GM_xmlhttpRequest({
	    method: "GET",
		url: urlMod,
		onload: function(response) {
		var responseHtml = new DOMParser().parseFromString (response.responseText, "text/html");
		document.getElementById("articleBody").innerHTML = responseHtml.getElementById("articleBody").innerHTML 
		    }
	});}