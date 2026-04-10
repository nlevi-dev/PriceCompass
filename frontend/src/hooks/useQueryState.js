import { useState, useEffect } from 'react';

export function useQueryState(key, initialValue, replace = true) {
    const [value, setValue] = useState(() => {
        const params = new URLSearchParams(window.location.search);
        const paramValue = params.get(key);
        if (paramValue !== null) {
            try { return JSON.parse(decodeURIComponent(paramValue)); } 
            catch (e) { return paramValue; }
        }
        return initialValue;
    });

    // Listen for Back/Forward button presses
    useEffect(() => {
        const handlePopState = () => {
            const params = new URLSearchParams(window.location.search);
            const paramValue = params.get(key);
            if (paramValue !== null) {
                try { setValue(JSON.parse(decodeURIComponent(paramValue))); } 
                catch (e) { setValue(paramValue); }
            } else {
                setValue(initialValue);
            }
        };

        window.addEventListener('popstate', handlePopState);
        return () => window.removeEventListener('popstate', handlePopState);
    }, [key, initialValue]);

    // Update URL when state changes
    useEffect(() => {
        const params = new URLSearchParams(window.location.search);
        const currentParam = params.get(key);
        const stringifiedValue = typeof value === 'object' ? JSON.stringify(value) : String(value);

        // Only update URL if the state is actually different from the URL
        if (currentParam !== stringifiedValue) {
            if (value === undefined || value === null || value === '') {
                params.delete(key);
            } else {
                params.set(key, stringifiedValue);
            }

            const newUrl = window.location.pathname + '?' + params.toString();
            if (replace) {
                window.history.replaceState(null, '', newUrl);
            } else {
                window.history.pushState(null, '', newUrl);
            }
        }
    }, [key, value, replace]);

    return [value, setValue];
}