odoo.define('work_trip.map2', function (require) {
    "use strict";

    $(document).ready(function(){


        function initMap() {
            const myLatlng = { lat: 21.125498, lng: 81.914063 };
            const map = new google.maps.Map(document.getElementById("map"), {
              zoom: 4,
              center: myLatlng,
            });
            // Create the initial InfoWindow.
          
            let infoWindow = new google.maps.InfoWindow({
              content: "Click the map to get Lat/Lng!",
              position: myLatlng,
            });
            infoWindow.open(map);
            // Configure the click listener.
            map.addListener("click", (mapsMouseEvent) => {
              // Close the current InfoWindow.
              infoWindow.close();
              // Create a new InfoWindow.
              infoWindow = new google.maps.InfoWindow({
                position: mapsMouseEvent.latLng,
              });
              infoWindow.setContent(
    
                JSON.stringify(mapsMouseEvent.latLng.toJSON(), null, 2)
              );
              const myObj = JSON.parse(JSON.stringify(mapsMouseEvent.latLng.toJSON(), null, 2));
    
              document.getElementById("lat").value=myObj.lat
              document.getElementById("long").value=myObj.lng
             
              infoWindow.open(map);
    
            });
    
          }
    
    });


});