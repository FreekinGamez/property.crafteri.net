import React, { useState, useEffect } from 'https://esm.sh/react';
import { createRoot } from 'https://esm.sh/react-dom/client';
import { Header, Footer } from '/headerfooter.js';
import { TableView } from '/tableview.js';

const PropertyCard = ({ property }) => {
  const roiIcon = property.roi >= 0 ? 'trending_up' : 'trending_down';
  return React.createElement('div', { className: 'property-card' },
    React.createElement('a', { 
      href: property.url, 
      target: '_blank', 
      rel: 'noopener noreferrer' 
    },
      React.createElement('div', { 
        className: 'property-image',
        style: { backgroundImage: `url(${property.image_url})` }
      })
    ),
    React.createElement('div', { className: 'property-content' },
      React.createElement('div', { className: 'property-header' },
        React.createElement('h3', { className: 'property-name' }, property.name),
        React.createElement('span', { className: 'property-district' }, property.district)
      ),
      React.createElement('div', { className: 'roi-section' },
        React.createElement('span', { className: 'roi-label' }, 'Annual ROI'),
        React.createElement('h2', { className: 'roi-value' },
          React.createElement('span', { className: 'material-icons roi-icon' }, roiIcon),
          `${property.roi}%`
        )
      ),
      React.createElement('div', { className: 'property-specs' },
        React.createElement('div', { className: 'specs-grid' },
          React.createElement('div', { className: 'spec-item' },
            React.createElement('span', { className: 'material-icons' }, 'bed'),
            React.createElement('span', { className: 'spec-value' }, property.beds)
          ),
          React.createElement('div', { className: 'spec-item' },
            React.createElement('span', { className: 'material-icons' }, 'bathtub'),
            React.createElement('span', { className: 'spec-value' }, property.baths)
          ),
          React.createElement('div', { className: 'spec-item' },
            React.createElement('span', { className: 'material-icons' }, 'square_foot'),
            React.createElement('span', { className: 'spec-value' }, property.int_m2)
          ),
          property.ext_m2 && React.createElement('div', { className: 'spec-item' },
            React.createElement('span', { className: 'material-icons' }, 'nature'),
            React.createElement('span', { className: 'spec-value' }, property.ext_m2)
          )
        )
      ),
      React.createElement('div', { className: 'property-price' },
        `£${parseInt(property.price).toLocaleString()}`
      )
    )
  );
};

const ViewModeSelector = ({ currentMode, onModeChange }) => {
  return React.createElement('div', { className: 'view-mode-selector' },
    React.createElement('button', {
      className: `view-mode-btn ${currentMode === 'grid' ? 'active' : ''}`,
      onClick: () => onModeChange('grid'),
      title: 'Grid View'
    }, React.createElement('span', { className: 'material-icons' }, 'grid_view')),
    React.createElement('button', {
      className: `view-mode-btn ${currentMode === 'table' ? 'active' : ''}`,
      onClick: () => onModeChange('table'),
      title: 'Table View'
    }, React.createElement('span', { className: 'material-icons' }, 'table_rows')),
    React.createElement('button', {
      className: `view-mode-btn ${currentMode === 'graph' ? 'active' : ''}`,
      onClick: () => onModeChange('graph'),
      title: 'Graph View'
    }, React.createElement('span', { className: 'material-icons' }, 'bar_chart')),
    React.createElement('button', {
      className: `view-mode-btn ${currentMode === 'news' ? 'active' : ''}`,
      onClick: () => onModeChange('news'),
      title: 'News View'
    }, React.createElement('span', { className: 'material-icons' }, 'newspaper'))
  );
};

const SortButton = ({ onSortChange, sortConfig }) => {
  const [isOpen, setIsOpen] = useState(false);
  const sortOptions = [
    { value: 'roi', label: 'ROI' },
    { value: 'price', label: 'Price' },
    { value: 'beds', label: 'Beds' },
    { value: 'baths', label: 'Baths' },
    { value: 'int_m2', label: 'Internal m²' },
    { value: 'ext_m2', label: 'External m²' }
  ];

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (!event.target.closest('.sort-container')) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return React.createElement('div', { className: 'sort-container' },
    React.createElement('div', {
      className: `sort-button filter-input ${sortConfig.field ? 'active' : ''}`,
      onClick: () => setIsOpen(!isOpen)
    },
      `Sort by: ${(sortOptions.find(opt => opt.value === sortConfig.field) || {}).label || 'None'}`,
      isOpen && React.createElement('div', { className: 'sort-dropdown' },
        sortOptions.map(option =>
          React.createElement('div', {
            key: option.value,
            onClick: () => {
              onSortChange(option.value);
              setIsOpen(false);
            },
            className: 'sort-option'
          }, option.label)
        )
      )
    ),
    React.createElement('button', {
      className: 'sort-direction filter-input',
      onClick: () => onSortChange(sortConfig.field, !sortConfig.ascending),
      style: { width: '40px', height: '40px' }
    }, sortConfig.ascending ? '↑' : '↓')
  );
};

const DistrictFilter = ({ properties, selectedDistricts, onChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const districts = [...new Set(properties.map(p => p.district))].sort();
  const districtCounts = districts.reduce((acc, district) => {
    acc[district] = properties.filter(p => p.district === district).length;
    return acc;
  }, {});

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (!event.target.closest('.district-filter')) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return React.createElement('div', { className: 'district-filter' },
    React.createElement('div', {
      className: `district-button filter-input ${selectedDistricts.length > 0 ? 'active' : ''}`,
      onClick: () => setIsOpen(!isOpen)
    }, `Districts (${selectedDistricts.length || 'All'})`),
    isOpen && React.createElement('div', { className: 'district-dropdown' },
      districts.map(district =>
        React.createElement('label', { key: district, className: 'district-option' },
          React.createElement('input', {
            type: 'checkbox',
            checked: selectedDistricts.includes(district),
            onChange: (e) => {
              const newSelection = e.target.checked
                ? [...selectedDistricts, district]
                : selectedDistricts.filter(d => d !== district);
              onChange(newSelection);
            }
          }),
          `${district} (${districtCounts[district]})`
        )
      )
    )
  );
};

const App = () => {
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDistricts, setSelectedDistricts] = useState([]);
  const [sortConfig, setSortConfig] = useState({ field: 'roi', ascending: false });
  const [viewMode, setViewMode] = useState('grid');
  const [selectedRows, setSelectedRows] = useState([]);

const handleRowSelect = (webId, isSelected) => {
  setSelectedRows(prev => 
    isSelected ? [...prev, webId] : prev.filter(id => id !== webId)
  );
};

const handleSelectAll = (isSelected) => {
  setSelectedRows(isSelected ? sortedProperties.map(p => p.web_id) : []);
};

const handleCopy = () => {
  const selectedProperties = sortedProperties.filter(p => 
    selectedRows.includes(p.web_id)
  );
  navigator.clipboard.writeText(JSON.stringify(selectedProperties, null, 2));
};

  const [filters, setFilters] = useState({
    minPrice: '',
    maxPrice: '',
    minROI: '',
    beds: 'all'
  });
  const [initialLoadComplete, setInitialLoadComplete] = useState(false);

  const INITIAL_LOAD_COUNT = 30;

  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const response = await fetch(`https://property.crafteri.net/api?limit=${INITIAL_LOAD_COUNT}`);
        const data = await response.json();
        setProperties(data);
        setLoading(false);
        setInitialLoadComplete(true);
      } catch (error) {
        console.error('Error:', error);
      }
    };
    fetchInitialData();
  }, []);

  useEffect(() => {
    if (initialLoadComplete) {
      const fetchAllData = async () => {
        try {
          const response = await fetch('https://property.crafteri.net/api');
          const data = await response.json();
          setProperties(data);
        } catch (error) {
          console.error('Error:', error);
        }
      };
      fetchAllData();
    }
  }, [initialLoadComplete]);

  const filteredProperties = properties.filter(property => {
    const price = parseFloat(property.price) || 0;
    return (
      (selectedDistricts.length === 0 || selectedDistricts.includes(property.district)) &&
      (!filters.minPrice || price >= parseFloat(filters.minPrice)) &&
      (!filters.maxPrice || price <= parseFloat(filters.maxPrice)) &&
      (!filters.minROI || parseFloat(property.roi) >= parseFloat(filters.minROI)) &&
      (filters.beds === 'all' || property.beds >= parseInt(filters.beds))
    );
  });

  const sortedProperties = [...filteredProperties].sort((a, b) => {
    const aValue = parseFloat(a[sortConfig.field]) || 0;
    const bValue = parseFloat(b[sortConfig.field]) || 0;
    return (aValue - bValue) * (sortConfig.ascending ? 1 : -1);
  });

  return React.createElement('div', { className: 'app' },
    React.createElement(Header),
    React.createElement('div', { className: 'filter-section' },
      React.createElement(DistrictFilter, {
        properties,
        selectedDistricts,
        onChange: setSelectedDistricts
      }),
      React.createElement('input', {
        type: 'number',
        placeholder: 'Min Price',
        className: `filter-input ${filters.minPrice ? 'active' : ''}`,
        onChange: (e) => setFilters({...filters, minPrice: e.target.value})
      }),
      React.createElement('input', {
        type: 'number',
        placeholder: 'Max Price',
        className: `filter-input ${filters.maxPrice ? 'active' : ''}`,
        onChange: (e) => setFilters({...filters, maxPrice: e.target.value})
      }),
      React.createElement('input', {
        type: 'number',
        placeholder: 'Min ROI %',
        className: `filter-input ${filters.minROI ? 'active' : ''}`,
        onChange: (e) => setFilters({...filters, minROI: e.target.value})
      }),
      React.createElement('select', {
        onChange: (e) => setFilters({...filters, beds: e.target.value}),
        className: `filter-input ${filters.beds !== 'all' ? 'active' : ''}`,
        value: filters.beds
      },
        React.createElement('option', { value: 'all' }, 'All Beds'),
        React.createElement('option', { value: '1' }, '1+ Beds'),
        React.createElement('option', { value: '2' }, '2+ Beds'),
        React.createElement('option', { value: '3' }, '3+ Beds')
      ),
      React.createElement(SortButton, {
        onSortChange: (field, ascending) => setSortConfig({ field, ascending }),
        sortConfig
      }),
      React.createElement(ViewModeSelector, {
        currentMode: viewMode,
        onModeChange: setViewMode
      })
    ),
    viewMode === 'grid' && React.createElement('div', { className: 'properties-grid' },
      loading 
        ? React.createElement('div', null, 'Loading...')
        : sortedProperties.map(property => 
            React.createElement(PropertyCard, { 
              key: property.id, 
              property 
            })
          )
    ),
    viewMode === 'table' && !loading && React.createElement(TableView, {
        properties: sortedProperties,
  	selectedRows,
  	onRowSelect: handleRowSelect,
  	onSelectAll: handleSelectAll,
  	onCopy: handleCopy
    }),
    viewMode === 'graph' && React.createElement('div', { className: 'placeholder-view' },
      React.createElement('h2', null, 'Graph View Coming Soon')
    ),
    viewMode === 'news' && React.createElement('div', { className: 'placeholder-view' },
      React.createElement('h2', null, 'News View Coming Soon')
    ),
    React.createElement(Footer)
  );
};

const root = createRoot(document.getElementById('root'));
root.render(React.createElement(App));
