import { X } from 'lucide-react';

const CloseButton = ({ onClick, size = 14, className = "", style = {} }) => {
    return (
        <button
            title="close"
            onClick={onClick}
            className={`inline-flex items-center justify-center rounded-md transition-all duration-200 hover:bg-gray-100 ${className}`}
            style={style}
            aria-label="List Links"
        >
            <X size={size} className="animate-in fade-in zoom-in duration-200" />
        </button>
    );
};
export default CloseButton;