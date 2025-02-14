import React, { useState, useEffect } from 'https://esm.sh/react';

const GraphView = ({ properties }) => {
  const [xAxis, setXAxis] = useState('price');
  const [yAxis, setYAxis] = useState('roi');
  const [graphType, setGraphType] = useState('scatter');
  const [graphData, setGraphData] = useState(null);

  const axisOptions = [
    { value: 'price', label: 'Price' },
    { value: 'roi', label: 'ROI' },
    { value: 'beds', label: 'Beds' },
    { value: 'baths', label: 'Baths' },
    { value: 'int_m2', label: 'Internal m²' },
    { value: 'ext_m2', label: 'External m²' }
  ];

  const graphTypes = [
    { value: 'scatter', label: 'Scatter Plot' },
    { value: 'line', label: 'Line Graph' },
    { value: 'bar', label: 'Bar Chart' },
    { value: 'pie', label: 'Pie Chart' }
  ];

  const calculateGraph = () => {
    // Here you would process the data based on selected axes and graph type
    // For now just store the raw data
    setGraphData({
      xAxis,
      yAxis,
      type: graphType,
      data: properties.map(p => ({
        x: parseFloat(p[xAxis]) || 0,
        y: parseFloat(p[yAxis]) || 0,
        label: p.name
      }))
    });
  };

  return React.createElement('div', { className: 'graph-view' },
    React.createElement('div', { className: 'graph-controls' },
      React.createElement('select', {
        value: xAxis,
        onChange: (e) => setXAxis(e.target.value),
        className: 'filter-input'
      },
        React.createElement('option', { value: '' }, 'Select X Axis'),
        axisOptions.map(opt => 
          React.createElement('option', { 
            key: opt.value, 
            value: opt.value 
          }, opt.label)
        )
      ),
      React.createElement('select', {
        value: yAxis,
        onChange: (e) => setYAxis(e.target.value),
        className: 'filter-input'
      },
        React.createElement('option', { value: '' }, 'Select Y Axis'),
        axisOptions.map(opt => 
          React.createElement('option', { 
            key: opt.value, 
            value: opt.value 
          }, opt.label)
        )
      ),
      React.createElement('div', { className: 'graph-type-selector' },
        graphTypes.map(type =>
          React.createElement('button', {
            key: type.value,
            className: `graph-type-btn ${graphType === type.value ? 'active' : ''}`,
            onClick: () => setGraphType(type.value)
          }, type.label)
        )
      ),
      React.createElement('button', {
        className: 'apply-button',
        onClick: calculateGraph
      }, 'Generate Graph')
    ),
    React.createElement('div', { className: 'graph-container' },
      graphData ? 
        React.createElement('div', { className: 'graph-placeholder' },
          `Graph will be rendered here with:`,
          React.createElement('pre', null, 
            JSON.stringify(graphData, null, 2)
          )
        ) :
        React.createElement('div', { className: 'graph-placeholder' },
          'Select axes and graph type, then click Generate Graph'
        )
    )
  );
};

export { GraphView };
