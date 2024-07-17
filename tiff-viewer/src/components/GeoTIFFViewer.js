import React, { useState, useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { fromArrayBuffer } from 'geotiff';
import axios from 'axios';
import * as Plot from '@observablehq/plot';

const GeoTIFFViewer = () => {
  const [contours, setContours] = useState(null);
  const svgRef = useRef(null);
  const plotRef = useRef(null);

  useEffect(() => {
    axios.get('http://localhost:8000/tiff', { responseType: 'arraybuffer' })
      .then(response => fromArrayBuffer(response.data))
      .then(tiff => tiff.getImage())
      .then(async image => {
        const width = image.getWidth();
        const height = image.getHeight();
        console.log('Width:', width);
        console.log('Height:', height);

        const rasters = await image.readRasters();
        console.log('rasters', rasters);
        let values = rasters[0]; // Assuming the first raster band contains the data

        // values = rotate(values, width, height);

        const { lons, lats } = extractGeoCoordinates(image, width, height);

        const contours = generateContours(values, width, height);
        setContours(contours);
        renderContours(contours, width, height, values, lons, lats);
      })
      .catch(error => console.error("Error loading TIFF:", error));
  }, []);

  const rotate = (values, width, height) => {
    const l = width >> 1;
    for (let j = 0, k = 0; j < height; ++j, k += width) {
      values.subarray(k, k + l).reverse();
      values.subarray(k + l, k + width).reverse();
      values.subarray(k, k + width).reverse();
    }
    return values;
  };

  const extractGeoCoordinates = (image, width, height) => {
    const [minLon, minLat, maxLon, maxLat] = image.getBoundingBox();

    const lons = [];
    const lats = [];
    for (let i = 0; i < height; i++) {
      for (let j = 0; j < width; j++) {
        const lon = minLon + (maxLon - minLon) * (j / width);
        const lat = maxLat - (maxLat - minLat) * (i / height); // 注意纬度方向与Y轴方向相反
        lons.push(lon);
        lats.push(lat);
      }
    }
    return { lons, lats };
  };

  const generateContours = (data, width, height) => {
    const values = new Array(height);
    for (let y = 0; y < height; y++) {
      values[y] = new Array(width);
      for (let x = 0; x < width; x++) {
        values[y][x] = data[y * width + x];
      }
    }

    const contours = d3.contours()
      .size([width, height])
      .smooth(true)
      .thresholds(d3.range(d3.min(data), d3.max(data), (d3.max(data) - d3.min(data)) / 10))(values.flat());

    return contours;
  };

  const renderContours = (contours, width, height, values, lons, lats) => {
    // Clear existing content
    d3.select(svgRef.current).selectAll("*").remove();
    d3.select(plotRef.current).selectAll("*").remove();

    if (contours.length === 0) {
      console.error("No contours generated");
      return;
    }

    // Plot rendering
    const color = d3.scaleSequential(d3.extent(values), d3.interpolateMagma);

    const plot = Plot.plot({
      projection: "mercator",
      color: { scheme: "Magma" },
      marks: [
        Plot.contour(values, {
          x: (_, i) => lons[i],
          y: (_, i) => lats[i],
          fill: Plot.identity,
          thresholds: 30,
          stroke: "#000",
          strokeWidth: 0.25,
          clip: "sphere"
        }),
        Plot.sphere()
      ]
    });

    plotRef.current.appendChild(plot);
  };

  return (
    <div>
      <h2>GeoTIFF Viewer</h2>
      <div ref={plotRef}></div>
      <svg ref={svgRef} width="5000" height="5000"></svg>
    </div>
  );
};

export default GeoTIFFViewer;
