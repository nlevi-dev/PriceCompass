import { Lock, LockOpen } from 'lucide-react';

const LockToggle = ({ isLinked, onToggle, size = 14, className = "" }) => {
    return (
        <button
            title="unlocking a row will allow changing the count of the items individually for all countries"
            onClick={() => onToggle(!isLinked)}
            className={`inline-flex items-center justify-center p-2 rounded-md transition-all duration-200 hover:bg-gray-100 ${
                isLinked ? 'text-blue-600' : 'text-black'
            } ${className}`}
            aria-label={isLinked ? "Unlink items" : "Link items"}
        >
            {isLinked ? (
                <Lock size={size} className="animate-in fade-in zoom-in duration-200" />
            ) : (
                <LockOpen size={size} className="animate-in fade-in zoom-in duration-200" />
            )}
        </button>
    );
};
export default LockToggle;