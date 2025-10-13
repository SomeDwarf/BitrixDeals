import { YMap, YMapDefaultSchemeLayer, YMapDefaultFeaturesLayer, YMapMarker, YMapListener } from './lib/ymaps.js'

const map = new YMap(
    document.getElementById('map'),
    {
        location: {
              center: [37.588144, 55.733842],
              zoom: 6
        }
    },
    [
        new YMapDefaultSchemeLayer({}),
        new YMapDefaultFeaturesLayer({})
    ]
);

const LABEL_ZOOM_THRESHOLD = 10;
let closeZoom = map.zoom >= LABEL_ZOOM_THRESHOLD;
const markers = [];

points.forEach(point => {
    const el = document.createElement('div');
    el.className = 'marker';

    const label = document.createElement('div');
    label.className = 'marker-label';
    label.innerText = point.title;
    label.style.display = 'none';
    el.appendChild(label);

    el.addEventListener('mouseenter', () => {
        label.style.display = 'block';
    });
    el.addEventListener('mouseleave', () => {
        if (!closeZoom) {
            label.style.display = 'none';
        }
    });

    const marker = new YMapMarker({ coordinates: point.coords }, el);
    map.addChild(marker);

    markers.push({ label });
});

map.addChild(new YMapListener({
    onUpdate: (event) => {
        const zoom = event.location.zoom;
        closeZoom = event.location.zoom >= LABEL_ZOOM_THRESHOLD
        markers.forEach(({ label }) => {
            label.style.display = closeZoom ? 'block' : 'none';
        });
    }
}));