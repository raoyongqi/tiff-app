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

        const rasters = await image.readRasters();
        let values = rasters[0]; // Assuming the first raster band contains the data

        // Filter out NaN or null values
        // values = values.map(value => isNaN(value) || value === 0 ? null : value);

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
    const colorScale = d3.scaleSequential()
        .domain(d3.extent(contours.map(c => c.value)))
        .interpolator(d3.interpolateMagma)
        .unknown("#fff"); // Set unknown values (NaN or null) to white
    
    // Add contours
    d3.select(svgRef.current)
        .selectAll("path")
        .data(contours)
        .enter().append("path")
        .attr("d", d3.geoPath())
        .attr("fill", d => colorScale(d.value))
        .attr("stroke", "#000")
        .attr("stroke-width", 0.5); // Adjust stroke width as needed

    // Extract colors used in the contours
    const usedColors = contours.map(c => colorScale(c.value));

    // Determine unique colors and create a scale for legend
    const uniqueColors = [...new Set(usedColors)];
    const legendWidth = 300;
    const legendHeight = 20;

    // Add color scale bar
    const defs = d3.select(svgRef.current).append("defs");
    const linearGradient = defs.append("linearGradient")
        .attr("id", "legend-gradient")
        .attr("x1", "0%").attr("y1", "0%")
        .attr("x2", "100%").attr("y2", "0%");

    // Add gradient stops based on colors used in the contours
    linearGradient.selectAll("stop")
        .data(uniqueColors)
        .enter().append("stop")
        .attr("offset", (d, i) => i / (uniqueColors.length - 1))
        .attr("stop-color", d => d);

    // Add legend rectangle
    const legend = d3.select(svgRef.current).append("g")
        .attr("class", "legend")
        .attr("transform", `translate(50, ${height + 100})`);

    legend.append("rect")
        .attr("width", legendWidth)
        .attr("height", legendHeight)
        .style("fill", "url(#legend-gradient)");

    // Create scale for legend
    const legendScale = d3.scaleLinear()
        .domain(d3.extent(contours.map(c => c.value)))
        .range([0, legendWidth]);

    // Add axis for legend
    const legendAxis = d3.axisBottom(legendScale)
        .ticks(5);

    legend.append("g")
        .attr("transform", `translate(0, ${legendHeight})`)
        .call(legendAxis);

    // Add legend label
    legend.append("text")
        .attr("x", legendWidth / 2)
        .attr("y", -6)
        .attr("fill", "#000")
        .attr("text-anchor", "middle")
        .text("Color Legend");

    // Add contours with updated styling
    const contoursGroup = d3.select(svgRef.current).append("g");

    contoursGroup.selectAll("path")
        .data(contours)
        .enter().append("path")
        .attr("d", d3.geoPath())
        .attr("fill", "none")
        .attr("stroke", "#000")
        .attr("stroke-width", 0.5)
        .attr("stroke-dasharray", "3,3") // Add dashed line style for contours
        .attr("stroke-opacity", 0.7); // Adjust opacity as needed

    // Optionally add labels to contours if applicable
    // contoursGroup.selectAll("text")
    //     .data(contours)
    //     .enter().append("text")
    //     .attr("transform", d => `translate(${d3.geoPath().centroid(d)})`)
    //     .attr("dy", "0.35em")
    //     .attr("text-anchor", "middle")
    //     .attr("font-size", 10)
    //     .text(d => d.value);

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
