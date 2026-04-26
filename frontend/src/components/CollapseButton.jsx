import { Triangle } from 'lucide-react';

const CollapseTrigger = ({ isOpen, onToggle, size = 14, className = "" }) => {
    return (
        <button
            type="button"
            title={isOpen ? "collapse" : "expand"}
            onClick={() => onToggle(!isOpen)}
            className={`inline-flex items-center justify-center p-2 rounded-md transition-colors hover:bg-gray-100 ${className}`}
            aria-expanded={isOpen}
        >
            <Triangle
                size={size}
                className={`fill-current transition-transform duration-200 ease-in-out ${
                    isOpen ? 'rotate-180' : 'rotate-90'
                }`}
            />
        </button>
    );
};
export default CollapseTrigger;