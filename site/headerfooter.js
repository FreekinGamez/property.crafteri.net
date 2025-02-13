import React from 'https://esm.sh/react';
export const Header = () => {
  return React.createElement('header', { className: 'header-container' },
    React.createElement('div', { className: 'header-content' },
      React.createElement('div', { className: 'header-left' },
        React.createElement('div', { className: 'logo-container' },
          React.createElement('span', { className: 'logo-text' }, 'crafteri'),
          React.createElement('span', { className: 'logo-dot' }, '.'),
          React.createElement('span', { className: 'logo-domain' }, 'net')
        ),
        React.createElement('div', { className: 'header-divider' })
      ),
      React.createElement('div', { className: 'header-main' },
        React.createElement('h1', { className: 'header-title' }, 'Gibraltar Property Intelligence'),
        React.createElement('p', { className: 'header-subtitle' }, 
          React.createElement('span', { className: 'material-icons' }, 'analytics'),
          'Strategic Investment Analysis'
        )
      ),
      React.createElement('div', { className: 'header-right' },
        React.createElement('div', { className: 'stats-container' },
          React.createElement('div', { className: 'stat-item' },
            React.createElement('span', { className: 'stat-label' }, 'Properties'),
            React.createElement('span', { className: 'stat-value' }, '234')
          ),
          React.createElement('div', { className: 'stat-item' },
            React.createElement('span', { className: 'stat-label' }, 'Avg. ROI'),
            React.createElement('span', { className: 'stat-value' }, '4.8%')
          )
        )
      )
    )
  );
};

export const Footer = () => {
  return React.createElement('footer', { className: 'footer' },
    React.createElement('div', { className: 'footer-content' },
      React.createElement('p', null, '© 2025 Crafteri Industries. All Rights Reserved.'),
      React.createElement('p', null,
        'Need help? Contact us at ',
        React.createElement('a', { href: 'mailto:info@crafteri.net' }, 'info@crafteri.net')
      )
    )
  );
};
