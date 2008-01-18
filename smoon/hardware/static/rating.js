function rating_displayHover(ratingId, star, img_over)
{
    for (var i = 0; i <= star; i++) {
	var starI = document.getElementById('star_'+ratingId+'_'+i);
	starI.setAttribute('src', img_over);
    }
}

function rating_displayNormal(ratingId, star, img_on, img_off)
{
    for (var i = 0; i <= star; i++) {
	var starI = document.getElementById('star_'+ratingId+'_'+i);
	if (starI.className == "on") {
	    starI.setAttribute('src', img_on);
	} else {
	    starI.setAttribute('src', img_off);
	}
    }
}

function rating_submitRating(href, widgetId, starNbr, maxnum, img_on, img_off)
{
    doSimpleXMLHttpRequest(href,
    { 'ratingID': widgetId, 'value': parseInt(starNbr)+1});

    for (var i = 0; i < maxnum; i++) {
	var star = document.getElementById('star_'+widgetId+'_'+i);
	if (i <= starNbr) {
	    star.setAttribute('src', img_on);
	    star.className = 'on';
	} else {
	    star.setAttribute('src', img_off);
	    star.className = 'off';
	}
    }
    displayHover(widgetId, starNbr);
}

function rating_init(href, maxnum, classname, img_on, img_off, img_over) {
    var ratings = document.getElementsByTagName('div');
    for (var i = 0; i < ratings.length; i++) {
	if (ratings[i].className != classname)
	    continue;
            
	var rating = ratings[i].firstChild.nodeValue;
	ratings[i].removeChild(ratings[i].firstChild);
	if (rating > maxnum)
	    rating = maxnum;
	if (rating < 0)
	    rating = 0;
	for (var j = 0; j < maxnum; j++) {
	    var star = document.createElement('img');
	    if (rating >= 1) {
		star.setAttribute('src', img_on);
		star.className = 'on';
		rating-=1;
	    }
	    else {
		star.setAttribute('src', img_off);
		star.className = 'off';
	    }
	    var widgetId = ratings[i].getAttribute('id');
	    star.setAttribute('id', 'star_'+widgetId+'_'+j);
	    star.onmouseover = new Function("env", "rating_displayHover('"+widgetId+"',"+j+",'"+img_over+"');");
	    star.onmouseout = new Function("env", "rating_displayNormal('"+widgetId+"',"+j+",'"+img_on+"','"+img_off+"');");
	    star.onclick = new Function("env", "rating_submitRating('"+href+"','"+widgetId+"',"+j+","+maxnum+",'"+img_on+"','"+img_off+"');");
	    ratings[i].appendChild(star);
	} 
    }
}

function single_rating_displayHover(ratingId, star, imgon_pre, img_post)
{
    var starI = document.getElementById('star_'+ratingId+'_'+star);
    if (starI.className == "off") {
	starI.setAttribute('src', imgon_pre+(parseInt(star))+img_post);
    }
}

function single_rating_displayNormal(ratingId, star, imgoff_pre, img_post)
{
    var starI = document.getElementById('star_'+ratingId+'_'+star);
    if (starI.className == "off") {
	starI.setAttribute('src', imgoff_pre + (parseInt(star)) + img_post);
    }
}


function single_rating_callBackRating(widgetId, starNbr, maxnum, imgon_pre, imgoff_pre, img_post)
{
    for (var i = 0; i <= maxnum; i++) {
	var star = document.getElementById('star_'+widgetId+'_'+i);
	if (i == starNbr) {
	    star.setAttribute('src', imgon_pre+i+img_post);
	    star.className = 'on';
	} else {
	    star.setAttribute('src', imgoff_pre+i+img_post);
	    star.className = 'off';
	}
    }
}

function single_rating_submitRating(href, widgetId, starNbr, maxnum, imgon_pre, imgoff_pre, imgbusy_pre, img_post)
{
    var oldStarNbr = starNbr;

    for (var i = 0; i <= maxnum; i++) {
	var star = document.getElementById('star_'+widgetId+'_'+i);
	if (star.className == 'on') {
	    oldStarNbr = i;
	}
	if (star.className == 'busy') {
	    return;
	}
    }

    var d = doSimpleXMLHttpRequest(href,
	{ 'ratingID': widgetId, 'value': parseInt(starNbr)});

    d.addCallback(new Function("env", "single_rating_callBackRating('"+widgetId+"',"+starNbr+","+maxnum+",'"+imgon_pre+"','"+imgoff_pre+"','"+img_post+"');"),
		  new Function("env", "single_rating_callBackRating('"+widgetId+"',"+oldStarNbr+","+maxnum+",'"+imgon_pre+"','"+imgoff_pre+"','"+img_post+"');"));

    for (var i = 0; i <= maxnum; i++) {
	var star = document.getElementById('star_'+widgetId+'_'+i);
	if (i == starNbr) {
	    star.setAttribute('src', imgbusy_pre+img_post);
	    star.className = 'busy';
	} else {
	    star.setAttribute('src', imgoff_pre+i+img_post);
	    star.className = 'off';
	}
    }
}

function single_rating_init(href, maxnum, classname, imgon_pre, imgoff_pre, imgbusy_pre, img_post) {
    var ratings = document.getElementsByTagName('div');
    for (var i = 0; i < ratings.length; i++) {
	if (ratings[i].className != classname)
	    continue;
            
	var rating = ratings[i].firstChild.nodeValue;
	ratings[i].removeChild(ratings[i].firstChild);
	if (rating > maxnum)
	    rating = maxnum;
	if (rating < 0)
	    rating = 0;
	for (var j = 0; j <= maxnum; j++) {
	    var star = document.createElement('img');
	    if (rating == j) {
		star.setAttribute('src', '/static/images/rating/r'+j+'.png');
		star.className = 'on';
	    }
	    else {
		star.setAttribute('src', '/static/images/rating/ro'+j+'.png');
		star.className = 'off';
	    }
	    var widgetId = ratings[i].getAttribute('id');
	    star.setAttribute('id', 'star_'+widgetId+'_'+j);
	    star.onmouseover = new Function("env", "single_rating_displayHover('"+widgetId+"',"+j+",'"+imgon_pre+"','"+img_post+"');");
	    star.onmouseout = new Function("env", "single_rating_displayNormal('"+widgetId+"',"+j+",'"+imgoff_pre+"','"+img_post+"');");
	    star.onclick = new Function("env", "single_rating_submitRating('"+href+"','"+widgetId+"',"+j+","+maxnum+",'"+imgon_pre+"','"+imgoff_pre+"','"+imgbusy_pre+"','"+img_post+"');");
	    ratings[i].appendChild(star);
	}
    }
}
