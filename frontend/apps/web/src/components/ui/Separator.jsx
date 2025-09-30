import React from 'react';
import PropTypes from 'prop-types';

const cn = (...classes) => classes.filter(Boolean).join(' ');

const Separator = ({ 
  orientation = 'horizontal',
  className = '',
  ...rest 
}) => {
  const orientationClasses = {
    horizontal: 'h-[1px] w-full',
    vertical: 'h-full w-[1px]',
  };

  return (
    <div
      className={cn(
        'shrink-0 bg-gray-200',
        orientationClasses[orientation],
        className
      )}
      {...rest}
    />
  );
};

Separator.propTypes = {
  orientation: PropTypes.oneOf(['horizontal', 'vertical']),
  className: PropTypes.string,
};

export default Separator;
export { Separator };
