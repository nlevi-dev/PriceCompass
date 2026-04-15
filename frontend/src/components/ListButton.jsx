import { Link } from 'lucide-react';

const ListButton = ({ onClick, size = 14, className = "" }) => {
    return (
        <button
            title="source"
            onClick={onClick}
            className={`inline-flex items-center justify-center p-2 rounded-md transition-all duration-200 hover:bg-gray-100 ${className}`}
            aria-label="List Links"
        >
            <Link size={size} className="animate-in fade-in zoom-in duration-200" />
        </button>
    );
};
export default ListButton;