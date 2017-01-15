GOOGLE_API_KEY = 'AIzaSyCMgw5bWf-ZIGIsUYcFgK8v5_4uQeJUTzE';
var mapMarkers = [];
var paths = [];

$(document).ready(function() {
	var map = L.map('map').setView([33.448376, -112.074036], 13);
	$('#map_right_col').hide();
	breakfastIcon = L.icon({
    iconUrl: '/static/img/breakfast.png',

    iconSize:     [32, 37], // size of the icon
    iconAnchor:   [16, 37], // point of the icon which will correspond to marker's location
    popupAnchor:  [0, 0] // point from which the popup should open relative to the iconAnchor
	});
	lunchIcon = L.icon({
    iconUrl: '/static/img/lunch.png',

    iconSize:     [32, 37], // size of the icon
    iconAnchor:   [16, 37], // point of the icon which will correspond to marker's location
    popupAnchor:  [0, 0] // point from which the popup should open relative to the iconAnchor
	});
	dinnerIcon = L.icon({
    iconUrl: '/static/img/dinner.png',

    iconSize:     [32, 37], // size of the icon
    iconAnchor:   [16, 37], // point of the icon which will correspond to marker's location
    popupAnchor:  [0, 0] // point from which the popup should open relative to the iconAnchor
	});
	activityIcon = L.icon({
    iconUrl: '/static/img/activity.png',

    iconSize:     [32, 37], // size of the icon
    iconAnchor:   [16, 37], // point of the icon which will correspond to marker's location
    popupAnchor:  [0, 0] // point from which the popup should open relative to the iconAnchor
	});


	L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
			attribution: 'Map data &copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
			maxZoom: 18,
			id: 'mapbox.satellite',
			accessToken: 'pk.eyJ1IjoiZ2VvZmZodyIsImEiOiJjaXh4a2d3Z3EwMDNrMnFsYWx3Z3Axd2R4In0.NYeciTJrObuu0VdFqR4D4w'
	}).addTo(map);

	toastr.options = {
	  "closeButton": false,
	  "debug": false,
	  "newestOnTop": false,
	  "progressBar": false,
	  "positionClass": "toast-bottom-center",
	  "preventDuplicates": true,
	  "onclick": null,
	  "showDuration": "300",
	  "hideDuration": "1000",
	  "timeOut": "5000",
	  "extendedTimeOut": "1000",
	  "showEasing": "swing",
	  "hideEasing": "linear",
	  "showMethod": "fadeIn",
	  "hideMethod": "fadeOut"
	}

	map.scrollWheelZoom.disable();

	var submitButton = $('#submit_button');
	var searchBar = $('#locationForm');

	submitButton.on('click', function() {
		console.log("submit clicked!");
		mapMarkers.forEach(function(marker) {
			map.removeLayer(marker);
		});
		paths.forEach(function(path) {
			map.removeLayer(path);
		});
		mapMarkers = [];
		paths = [];
		$('#list-group').html('');
		$('#map_left_col').removeClass('col-md-9');
		$('#map_right_col').hide();
		map._onResize();

		var terms = $('#terms').val()

		submitButton.attr("disabled", true);

		/*if ($('#museum').is(":checked"))
			terms.push("museum");
		if ($('#sports').is(":checked"))
			terms.push("sports");
		if ($('#music').is(":checked"))
			terms.push("music");*/

		console.log(terms);
		address = searchBar.val();
		var latitude = 0;
		var longitude = 0;

		toastr.success('Your schedule is being generated. Please be patient.', 'Loading...')

		$.ajax({
	      url: generateGoogleURL(address),
	      success: function (data) {
	        if(data.results.length > 0) {
	        	var location = data.results[0].geometry.location;
						latitude = location.lat;
						longitude = location.lng;
	        }
	      }
	  }).done(function() {
			getDataFromServer(terms, latitude, longitude, function(json) {
				console.log(json);
				var morningActivities = json.morning_activities;
				var afternoonActivities = json.afternoon_activities;

				var breakfast = json.breakfast;
				var lunch = json.lunch;
				var dinner = json.dinner;

				var schedule = [];
				schedule.push(breakfast);
				appendArray(schedule, morningActivities);
				schedule.push(lunch);
				appendArray(schedule, afternoonActivities);
				schedule.push(dinner);
				console.log(schedule);
				for(var i = 0; i < schedule.length; i++) {
					var marker = null;
					if(i == 0) {
						marker = addMarker(map, schedule[i], breakfastIcon);
					} else if(i == 3) {
						marker = addMarker(map, schedule[i], lunchIcon);
					} else if(i == 6) {
						marker = addMarker(map, schedule[i], dinnerIcon);
					} else {
						marker = addMarker(map, schedule[i], activityIcon);
					}

					mapMarkers.push(marker);

					if(i != 0) {
						var prev = schedule[i - 1];
						var curr = schedule[i];

						var polyline = createPath(map, prev.latitude, prev.longitude, curr.latitude, curr.longitude);
						paths.push(polyline);
					}
				}
				$('#map_left_col').addClass('col-md-9');
				$('#map_right_col').show();

				scrollToMap();
				var group = new L.featureGroup(mapMarkers);
				map.fitBounds(group.getBounds().pad(0.0));

				submitButton.attr("disabled", false);
			});
		});
	});
});

function scrollToMap() {
	$('html, body').animate({
        scrollTop: $("#map_section").offset().top - 100
    }, 2000);
}

function addMarker(map, activity, icon){
	console.log("addMarker called.");

	var marker = L.marker([activity.latitude, activity.longitude], {icon: icon}).addTo(map);
	var popupHTML = '<div class="marker-popup">';

	if(activity.image_list != null) {
		popupHTML += '<img class="popup-image" src="' + activity.image_list + '">'
	}

	popupHTML += "<b>" + activity.name + "</b>";

	if(activity.rating != null) {
		popupHTML += "<b> (" + activity.rating + "/5 rating)</b><br><br>"
	}

	/*popupHTML += '<div class="progress"><div class="progress-bar" role="progressbar" style="width: 15%" aria-valuenow="' + activity.rating + '" aria-valuemin="0" aria-valuemax="5"></div></div>';*/
	if(activity.description != null) {
		popupHTML += activity.description;
	}
	popupHTML += '</div>';

	addListElement(activity);
	marker.bindPopup(popupHTML);

	marker.index = mapMarkers.length;
	marker.on('click', function(event) {
		var enclosingListGroup = $('#list-group');
		resetListColoring(enclosingListGroup);
		enclosingListGroup.children().eq(this.index).addClass('active');
		console.log(this.index);
	});

	return marker;
}

function addListElement(activity) {
	console.log("addListElement called.");
	var enclosingListGroup = $('#list-group');
	var numElements = enclosingListGroup.children().length;

	var listElement = document.createElement("li");
	listElement.setAttribute("class", "list-group-item");
	listElement.setAttribute("count", numElements);

	/*if(numElements == 0 || numElements == 3 || numElements == 6) {
		listElement.setAttribute("class", "purple-border");
	} else {
		listElement.setAttribute("class", "green-border");
	}*/

	listElement.innerHTML = "<h5>" + (numElements + 1) + ". " + activity.name + "</h5>";

	listElement.addEventListener('click', function() {
		resetListColoring(enclosingListGroup);
		var index = parseInt(listElement.getAttribute('count'));
		enclosingListGroup.children().eq(index).addClass("active");
		mapMarkers[index].openPopup();
	});

	enclosingListGroup.append(listElement);
}

function resetListColoring(enclosingListGroup){
	enclosingListGroup.children().removeClass("active");
}

function createPath(map, lat1, long1, lat2, long2){
	coords = [[lat1, long1], [lat2, long2]];

	var polyline = L.polyline(coords).addTo(map);
	return polyline;
}

function appendArray(mainArray,  arrayToAdd) {
	for (var i = 0 ; i < arrayToAdd.length; i++) {
		mainArray.push(arrayToAdd[i]);
	}
}

function getDataFromServer(terms, latitude, longitude, cb){
	var xhr = new XMLHttpRequest();

	var url = "simulate?"
			   		+ "lat=" + latitude + "&long=" + longitude;

	if(terms != '') {
		url += "&terms=" + terms;
	}

	console.log(url);

	xhr.onload = function() {
		var response = xhr.responseText;
		var json = JSON.parse(response);
		cb(json);
	}
	xhr.open("GET", url);

	xhr.send();
}

function generateGoogleURL(address) {
	var url = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + encodeURI(address) + '&key=' + GOOGLE_API_KEY;
	return url;
}
