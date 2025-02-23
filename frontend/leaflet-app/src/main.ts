import "leaflet/dist/leaflet.css";
import L from "leaflet";
import * as geojson from "geojson";
import stc from "string-to-color";

import "./style.css";

document.querySelector<HTMLDivElement>("#app")!.innerHTML = `
  <div id="map"></div>
`;

const map = L.map("map").setView([0, 0], 3);
const groups: {
  [topic: string]: {
    markers: L.Marker[];
    polygons: L.GeoJSON[];
    points: L.Point[];
  };
} = {};

// const bgLayer = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
//   maxZoom: 19,
//   attribution:
//     '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
// });
// bgLayer.addTo(map);

async function fetchGeoJson(name: string) {
  const res = await fetch(`/geojson/${name}.geojson`);
  return res;
}

const res = await fetchGeoJson("convex");
const data = await res.json();
const convexLayer = L.geoJSON(data, {
  style: {
    weight: 2,
    fillOpacity: 0.5,
    opacity: 1,
  },
  onEachFeature: function (feature, layer) {
    const featureType = feature.geometry.type;
    const featureTopic = feature.properties?.Topic;

    // Create topic in groups if not exists
    if (!groups[featureTopic]) {
      groups[featureTopic] = { markers: [], points: [], polygons: [] };
    }
    const topicGroup = groups[featureTopic];

    if (featureType === "Polygon") {
      const centroid = L.geoJSON(feature).getBounds().getCenter();

      const textIcon = L.divIcon({
        className: "topic-text-container",
        // html: feature.properties.Topic,
        // html: `<b class="topic-text" style="color: ${stc(featureTopic)};">${
        //   feature.properties.Topic
        // }</b>`,
        html: `<b class="topic-text">${feature.properties.Topic}</b>`,
        iconSize: [0, 0], // No default marker size
        iconAnchor: [0, 0],
      });
      const marker = L.marker(centroid, {
        icon: textIcon,
      });
      topicGroup.markers.push(marker);
      marker.addTo(map);

      const polygon = L.geoJSON(feature, {
        style: {
          color: stc(featureTopic),
          fillOpacity: 0.5,
          opacity: 1,
          weight: 2,
        },
        // onEachFeature: (feature, layer) => {
        // layer.on("mousemove", (e: L.LeafletMouseEvent) => {
        //   const target = e.target;
        //   target.setStyle({ fillOpacity: 0.8 });
        // });
        // },
      });
      topicGroup.polygons.push(polygon);
      polygon.addTo(map);
    } else if (featureType === "MultiPolygon") {
      feature.geometry.coordinates.forEach((coords) => {
        const centroid = L.geoJSON({ type: "Polygon", coordinates: coords })
          .getBounds()
          .getCenter();

        const textIcon = L.divIcon({
          className: "topic-text-container",
          // html: feature.properties.Topic,
          // html: `<b class="topic-text
          // " style="color: ${stc(featureTopic)};">${
          //   feature.properties.Topic
          // }</b>`,
          html: `<b class="topic-text
          " >${feature.properties.Topic}</b>`,
          iconSize: [0, 0], // No default marker size
          iconAnchor: [0, 0],
        });
        const marker = L.marker(centroid, {
          icon: textIcon,
        });
        topicGroup.markers.push(marker);
        marker.addTo(map);
      });

      const polygon = L.geoJSON(feature, {
        style: {
          color: stc(featureTopic),
          fillOpacity: 0.5,
          opacity: 1,
          weight: 2,
        },
      });
      topicGroup.polygons.push(polygon);
      polygon.addTo(map);
    }

    // convexGroup[feature.properties?.Topic].push();

    // const centroid = feature.geometry.coordinates;
    // console.log(centroid);

    // const textIcon = L.divIcon({
    //   className: "custom-text",
    //   html: `<b>${feature.properties.name}</b>`,
    //   iconSize: [0, 0], // No default marker size
    // });

    // L.marker(centroid, { icon: textIcon }).addTo(map);
  },
});
// convexLayer.addTo(map);

const res1 = await fetchGeoJson("points");
const data1 = await res1.json();
const pointsLayer = L.geoJSON(data1, {
  onEachFeature: function (feature, layer) {
    // const featureType = feature.geometry.type;
    // const featureTopic = feature.properties?.Topic;

    // // Create topic in groups if not exists
    // if (!groups[featureTopic]) {
    //   groups[featureTopic] = { markers: [], points: [], polygons: [] };
    // }
    // const topicGroup = groups[featureTopic];

    // if (featureType === "Point") {

    // }

    if (!feature.properties?.Url) return;

    layer.bindTooltip(feature.properties.Url, {
      // permanent: true,
      direction: "top",
    });
  },
});
// pointsLayer.addTo(map);

map.on("zoomend", function () {
  const pointsZoomedIn = map.getZoom() > 7;
  const textZoomedIn = map.getZoom() > 4;

  if (pointsZoomedIn) {
    pointsLayer.addTo(map);
  } else {
    pointsLayer.removeFrom(map);
  }

  Object.keys(groups).forEach((topicName) => {
    const topic = groups[topicName];
    topic.markers.forEach((layer: L.Marker) => {
      layer.setOpacity(textZoomedIn ? (pointsZoomedIn ? 0.3 : 1) : 0);
    });
    topic.polygons.forEach((layer: L.GeoJSON) => {
      layer.setStyle({
        opacity: pointsZoomedIn ? 0.3 : 1,
        fillOpacity: pointsZoomedIn ? 0.1 : 0.5,
      });
    });
  });
});
