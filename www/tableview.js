import React from 'https://esm.sh/react';

export const TableView = ({ properties, selectedRows, onRowSelect, onSelectAll, onCopy }) => {
  return React.createElement('div', { className: 'table-view' },
    React.createElement('div', { className: 'table-controls' },
      React.createElement('label', { className: 'select-all' },
        React.createElement('input', {
          type: 'checkbox',
          onChange: (e) => onSelectAll(e.target.checked),
          checked: selectedRows.length === properties.length
        }),
        'Select All'
      ),
      React.createElement('button', {
        className: 'copy-button',
        onClick: onCopy
      }, React.createElement('span', { 
        className: 'material-icons'
      }, 'content_copy'))
    ),
    React.createElement('table', null,
      React.createElement('thead', null,
        React.createElement('tr', null,
          React.createElement('th', null),
          React.createElement('th', null, 'Name'),
          React.createElement('th', null, 'District'),
          React.createElement('th', null, 'ROI'),
          React.createElement('th', null, 'Price'),
          React.createElement('th', null, 'Beds'),
          React.createElement('th', null, 'Baths'),
          React.createElement('th', null, 'Int. m²'),
          React.createElement('th', null, 'Ext. m²')
        )
      ),
      React.createElement('tbody', null,
        properties.map(property => 
          React.createElement('tr', { key: property.web_id },
            React.createElement('td', null,
              React.createElement('input', {
                type: 'checkbox',
                checked: selectedRows.includes(property.web_id),
                onChange: (e) => onRowSelect(property.web_id, e.target.checked)
              })
            ),
            React.createElement('td', null, property.name),
            React.createElement('td', null, property.district),
            React.createElement('td', null, `${property.roi}%`),
            React.createElement('td', null, `£${parseInt(property.price).toLocaleString()}`),
            React.createElement('td', null, property.beds),
            React.createElement('td', null, property.baths),
            React.createElement('td', null, property.int_m2),
            React.createElement('td', null, property.ext_m2 || '-')
          )
        )
      )
    )
  );
};
