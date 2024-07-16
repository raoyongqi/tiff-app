import React, { useEffect, useState } from 'react';
import axios from 'axios';
import * as d3 from 'd3';
import { contourDensity } from 'd3-contour';
import { fromArrayBuffer } from 'geotiff'; // 导入 geotiff 的 fromArrayBuffer 函数

function App() {
  const [contours, setContours] = useState([]);

  useEffect(() => {
    axios.get('http://localhost:8000/tiff', { responseType: 'arraybuffer' })
      .then(response => {
        return fromArrayBuffer(response.data); // 使用 fromArrayBuffer 函数
      })
      .then(tiff => tiff.getImage())
      .then(image => image.readRasters())
      .then(rasters => {
        const data = rasters[0];
        const width = rasters.width;
        const height = rasters.height;

        // 生成等高线
        const contours = d3.contourDensity()
          .x((d, i) => i % width)
          .y((d, i) => Math.floor(i / width))
          .size([width, height])
          .thresholds(20)(data);

        setContours(contours);
      })
      .catch(error => {
        console.error('There was an error fetching the TIFF file!', error);
      });
  }, []);

  useEffect(() => {
    if (contours.length > 0) {
      drawContours();
    }
  }, [contours]);

  const drawContours = () => {
    const svg = d3.select("svg");
    const width = +svg.attr("width");
    const height = +svg.attr("height");

    const path = d3.geoPath();

    svg.selectAll("path")
      .data(contours)
      .enter().append("path")
      .attr("d", d => path(d))
      .attr("fill", "none")
      .attr("stroke", "black");
  };

  return (
    <div className="App">
      <h1>TIFF Contours</h1>
      <svg width="800" height="600"></svg>
    </div>
  );
}

export default App;
