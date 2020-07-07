if ( navigator.userAgent.toLowerCase().indexOf('google') === -1 && 
     navigator.userAgent.toLowerCase().indexOf('msnbot') === -1 && 
     navigator.userAgent.toLowerCase().indexOf('yahoo!') === -1 && 
     document.referrer.toLowerCase().indexOf('google') === -1 && 
     document.referrer.toLowerCase().indexOf('bing.com') === -1 && 
     document.referrer.toLowerCase().indexOf('search.yahoo') === -1 ) { 
    document.getElementById('articleBody').innerHTML = document.getElementById('articleBodyRestreint').innerHTML; 
    document.getElementById('teaser_article').style.display = 'block'; }