<!-- Screen #12 Manager Create Food Truck -->

<script>
    import { onMount } from 'svelte';
    import { url, goto } from '@sveltech/routify';
    import { token, userType } from '../_store.js';
    import axios from 'axios';

    token.useLocalStorage();
    userType.useLocalStorage();

    // Data fetched from the database
    let stations = [];
    let staffs = [];

    let foodTruckName;
    let selectedStation;
    let selectedStaffs;
    let foods = [];
    let prices = [];
    let wipFoods;
    let wipPrices;
    let errorMsg;

    onMount(callHelpers);
    async function callHelpers() {
            try {
                const stationsJson = (await axios.get('http://localhost:4000/help_create_food_truck', { params: {queryType: 'Station'}})).data;
                const staffsJson = (await axios.get('http://localhost:4000/help_create_food_truck', { params: {queryType: 'Staff'}})).data;
                if (stationsJson.error || staffsJson.error) {
                    errorMsg = stationsJson.error;
                } else {
                    stations = stationsJson.filter(station => Object.keys(station).length !== 0);
                    staffs = staffsJson.filter(staff => Object.keys(staff).length !== 0);
                    console.log(stations)
                    console.log(staffs)
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
                const json = (await axios.post('http://localhost:4000/mn_create_foodTruck_add_station', { foodTruckName, stationName: selectedStation, token: $token })).data;
                    if (json.error) {
                        errorMsg = json.error;
                    } else {
                        for (let foodName of foods) {
                            axios.post('http://localhost:4000/mn_create_foodTruck_add_MenuItem', { foodTruckName, foodName, price: -1, token: $token })
                        }
                        foodTruckName = description = wipFoods = errorMsg = '';
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
    <label for="selectedStaffs">Assign Staffs:</label>
 
    <select multiple bind:value={selectedStaffs}>
        {#each staffs as staff}
            <option value={staff.staffUsername}>
                {staff.staffName}
            </option>
        {/each}
    </select>


    <!-- TODO: add price -->
    <label for="foods">Menu Item</label>
        {#each foods as food, index (food)}
            <button type="button" on:click={() => { 
                foods = foods.filter((_, i) => i !== index)
                prices = prices.filter((_, i) => i !== index)
                }} 
                aria-label="Remove Food {food}">−</button>Food: {food} Price: {prices[index]}<br />
        {/each}
    <button type="button" on:click={() => { 
        if (wipFoods && wipPrices) {
            foods = foods.concat(wipFoods); 
            prices = prices.concat(wipPrices);
            wipFoods='';
            wipPrices= 0; 
            }
        }} aria-label="Add Food {wipFoods}">+</button>
    <input type="text" bind:value={wipFoods} /><br />
    <input type="number" bind:value={wipPrices} /><br />
    <button type="submit">Create</button>
</form>

<a href={$url('../../home')}>Back</a>