import { writable } from 'svelte/store';

function persistentWritable(key, startValue) {
    const { subscribe, set } = writable(startValue);

    return {
        subscribe,
        set,
        useLocalStorage: () => {
            const json = localStorage.getItem(key);
            if (json) {
                set(JSON.parse(json));
            }
    
            subscribe(current => {
                localStorage.setItem(key, JSON.stringify(current));
            });
        }
    };
}

export const token = persistentWritable('FoodTruck token', '');
export const userType = persistentWritable('FoodTruck userType', '');

// TODO: use cookies instead of storing token in localStorage