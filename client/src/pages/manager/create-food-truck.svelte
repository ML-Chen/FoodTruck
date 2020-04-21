<!-- Screen #12 Manager Create Food Truck -->

<script>
    import { onMount } from 'svelte';
    import { url, goto } from '@sveltech/routify';
    import { token, userType, storeUsername } from '../_store.js';
    import axios from 'axios';

    token.useLocalStorage();
    userType.useLocalStorage();
    storeUsername.useLocalStorage();


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
    let managerUsername = $storeUsername

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
        } else if (!selectedStation) {
            errorMsg = 'Please select a station';
        } else if (!selectedStaffs) {
            errorMsg = 'Please assign at least one staff';
        } else if (foods == []) {
            errorMsg = 'Please add at least one food'; 
        } else {
            try {
                const json = (await axios.post('http://localhost:4000/mn_create_foodTruck_add_station', { foodTruckName, stationName: selectedStation, managerUsername: $storeUsername, token: $token })).data;    
                for (let i = 0; i < foods.length; i++) {
                    console.log(foods[i]);
                    console.log(prices[i]);
                    axios.post('http://localhost:4000/mn_create_foodTruck_add_MenuItem', { foodTruckName, foodName: foods[i], price: prices[i], managerUsername: $storeUsername, token: $token })
                }
                foodTruckName = description = wipFoods = errorMsg = '';
                foods = [];
                    
            } catch (error) {
                console.log(error);
                errorMsg = error.response;
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
            if (wipFoods in foods) {
                errorMsg = "Duplicate Food name"
            } else {
                foods = foods.concat(wipFoods); 
                prices = prices.concat(wipPrices);
                wipFoods='';
                wipPrices= 0;
                } 
            }
        }} aria-label="Add Food {wipFoods}">+</button>
    <input type="text" bind:value={wipFoods} /><br />
    <input type="number" bind:value={wipPrices} /><br />
    <button type="submit">Create</button>
    <p>{errorMsg}</p>
    <h1>{selectedStaffs}</h1>
    <h1>{selectedStation}</h1>
</form>

<a href={$url('../../home')}>Back</a>