import { writable } from 'svelte/store';

function persistentWritable(key, startValue) {
    const { subscribe, set } = writable(startValue);

    return {
        subscribe,
        set,
        useLocalStorage: () => {
            const json = localStorage.getItem(key);
            if (json && json !== "undefined" && json != null) {
                set(JSON.parse(json));
            }
    
            subscribe(current => {
                localStorage.setItem(key, JSON.stringify(current));
            });
        }
    };
}

export const token = persistentWritable('token', '');
export const userType = persistentWritable('userType', '');

// TODO: use cookies instead of storing token in localStorage