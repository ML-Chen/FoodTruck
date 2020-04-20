<!-- Screen #12 Manager Create Food Truck -->
<!-- Screen 5: Create foodTruck -->

<script>
    import { url, goto } from '@sveltech/routify';
    import { token, userType } from '../_store.js';
    import axios from 'axios';

    token.useLocalStorage();
    userType.useLocalStorage();

    // Data fetched from the database
    let stations;
    let staffs;

    let foodTruckName;
    let selectedStation;
    let foods = [];
    let wipFoods;
    let errorMsg;

    async function callHelpers() {
            try {
                const stationsJson = (await axios.post('http://localhost:4000/ad_create_foodTruck', { foodTruckName, description, token: $token })).data;
                const staffsJson = (await axios.post('http://localhost:4000/ad_create_foodTruck', { foodTruckName, description, token: $token })).data;
                if (stationsJson.error || staffsJson.error) {
                    errorMsg = stationsJson.error;
                } else {
                    stations = stationsJson.filter(station => Object.keys(station).length !== 0);
                    staffs = staffsJson.filter(staff => Object.keys(staff).length !== 0);
                }
            } catch (error) {
                console.log(error.response.data)
                errorMsg = error.response.data.error;
            }
    }
    async function createfoodTruck() {
        if (!foodTruckName) {
            errorMsg = 'foodTruck name must not be blank';
        } else if (!description) {
            errorMsg = 'Description must not be blank';
        } else {
            try {
                const json = (await axios.post('http://localhost:4000/ad_create_foodTruck', { foodTruckName, description, token: $token })).data;
                    if (json.error) {
                        errorMsg = json.error;
                    } else {
                        for (let Food of foods) {
                            axios.post('http://localhost:4000/ad_add_foodTruck_Food', { foodTruckName, Food, token: $token })
                        }
                        foodTruckName = description = wipFood = errorMsg = '';
                        foods = [];
                    }
            } catch (error) {
                console.log(error.response.data)
                errorMsg = error.response.data.error;
            }
        }
    }
</script>

<svelte:head>Create Food Truck</svelte:head>

<h1>Create Food Truck</h1>

<form on:submit|preventDefault={createfoodTruck}>
    <label for="foodTruckName">Name</label>
    <input type="text" id="foodTruckName" name="foodTruckName" bind:value={foodTruckName} />

    <select id="station-name" name="station-name" bind:value={selectedStation}>
        {#if stations}
            {#each stations.map(station => station.stationName) as sName}
                <option value={sName}>{sName}</option>
            {/each}
        {/if}
    </select>

    <label for="foods">Menu Item</label>
        {#each foods as food, index (food)}
            <button type="button" on:click={() => { foods = foods.filter((_, i) => i !== index) }} aria-label="Remove Food {food}">−</button>{food}<br />
        {/each}
    <button type="button" on:click={() => { if (wipFoods) { foods = foods.concat(wipFoods); wipFoods=''; }}} aria-label="Add Food {wipFoods}">+</button>
    <input type="text" bind:value={wipFoods} /><br />
    <button type="submit">Create</button>
</form>

<a href={$url('../../home')}>Back</a>