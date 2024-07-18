import React, { useState, useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { fromArrayBuffer } from 'geotiff';
import axios from 'axios';

const GeoTIFFViewer = () => {
  const [contours, setContours] = useState(null);
  const svgRef = useRef(null);
  const scaleRef = useRef(null); // Ref for scale group

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://localhost:8000/tiff', {
          responseType: 'arraybuffer',
          headers: {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Expires': '0'
          }
        });

        const tiff = await fromArrayBuffer(response.data);
        const image = await tiff.getImage();
        const width = image.getWidth();
        const height = image.getHeight();
        console.log('Width:', width);
        console.log('Height:', height);

        const rasters = await image.readRasters();
        console.log('rasters', rasters);
        let values = rasters[0]; // Assuming the first raster band contains the data

        // Filter out NaN or null values
        console.log("orin:",values)
        console.log(values)
        const contours = generateContours(values, width, height);
        setContours(contours);
        renderContours(contours, width, height);
      } catch (error) {
        console.error("Error loading TIFF:", error);
      }
    };

    fetchData();
  }, []);

  const generateContours = (data, width, height) => {
    const values = new Array(height);
    for (let y = 0; y < height; y++) {
      values[y] = new Array(width);
      for (let x = 0; x < width; x++) {
        values[y][x] = data[y * width + x];
      }
    }

    const validValues = data.filter(d => d !== null);
    const contours = d3.contours()
      .size([width, height])
      .smooth(true)
      .thresholds(d3.range(d3.min(validValues), d3.max(validValues), (d3.max(validValues) - d3.min(validValues)) / 10))(validValues);

    return contours;
  };

  const renderContours = (contours, width, height) => {
    // Clear existing content
    d3.select(svgRef.current).selectAll("*").remove();

    // Create color scale
    const color = d3.scaleSequential()
      .domain(d3.extent(contours.map(c => c.value)))
      .interpolator(d3.interpolateMagma)
      .unknown("#fff"); // Set unknown values (NaN or null) to white
    
    // Add contours
    d3.select(svgRef.current)
      .selectAll("path")
      .data(contours)
      .enter().append("path")
      .attr("d", d3.geoPath())
      .attr("fill", d => color(d.value))
      .attr("stroke", "#000")
      .attr("stroke-width", 0.25);

    // Add scale
    const scale = d3.scaleLinear()
      .domain(d3.extent(contours.map(c => c.value)))
      .range([20, 300]); // Scale range from 20 to 300 pixels

    const xAxis = d3.axisBottom(scale)
      .ticks(5); // Adjust number of ticks as needed

    d3.select(scaleRef.current)
      .attr("transform", `translate(50, 10)`) // Adjust position as needed
      .call(xAxis);
  };

  return (
    <div>
      <h2>GeoTIFF Viewer with d3</h2>
      <svg ref={svgRef} width="500" height="500">
        <g ref={scaleRef}></g>
      </svg>
    </div>
  );
};

export default GeoTIFFViewer;
