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
    let stations = []; // string[]
    let staffs = []; // [{staffUsername: string, staffName: string}]
    let foods = []; // string[]

    let foodTruckName;
    let selectedStation;
    let selectedStaffs;
    let selectedFoods = [];
    let prices = []; // number[]
    let wipFood; // string
    let wipPrice;
    let errorMsg;
    let managerUsername = $storeUsername

    onMount(callHelpers);
    async function callHelpers() {
        try {
            const stationsJson = (await axios.get('http://localhost:4000/help_create_food_truck', { params: {queryType: 'Station'}})).data;
            const staffsJson = (await axios.get('http://localhost:4000/help_create_food_truck', { params: {queryType: 'Staff'}})).data;
            const foodsJson = (await axios.get('http://localhost:4000/help_create_food_truck', { params: {queryType: 'Food'}})).data;
            if (stationsJson.error || staffsJson.error) {
                errorMsg = stationsJson.error;
            } else {
                stations = stationsJson.map(station => station.stationName);
                staffs = staffsJson;
                foods = foodsJson.map(food => food.foodName);
                selectedStation = stations.length > 0 ? stations[0] : null;
                wipFood = stations.length > 0 ? foods[0] : null;
                console.log(stations)
                console.log(staffs)
                console.log(foods)
            }
        } catch (error) {
            console.log(error);
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
        } else if (selectedFoods.length === 0) {
            errorMsg = 'Please add at least one food'; 
        } else {
            try {
                const json = (await axios.post('http://localhost:4000/mn_create_foodTruck_add_station', { foodTruckName, stationName: selectedStation, managerUsername: $storeUsername, token: $token })).data;    
                for (let i = 0; i < selectedFoods.length; i++) {
                    console.log(selectedFoods[i]);
                    console.log(prices[i]);
                    await axios.post('http://localhost:4000/mn_create_foodTruck_add_MenuItem', { foodTruckName, foodName: selectedFoods[i], price: prices[i], managerUsername: $storeUsername, token: $token })
                }
                for (let i = 0; i < selectedStaffs.length; i++) {
                    console.log(selectedStaffs[i]);
                    await axios.post('http://localhost:4000/mn_create_foodTruck_add_staff', { foodTruckName, staffName: selectedStaffs[i], managerUsername: $storeUsername, token: $token })
                }
                foodTruckName = wipFood = errorMsg = '';
                selectedFoods = [];
                    
            } catch (error) {
                console.log(error);
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
            {#each stations as sName}
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

    <label for="selectedFoods">Menu Item (name and price)</label>
        {#each selectedFoods as selectedFood, index (selectedFood)}
            <button type="button" on:click={() => { 
                selectedFoods = selectedFoods.filter((_, i) => i !== index)
                prices = prices.filter((_, i) => i !== index)
                foods = foods.concat(selectedFood)
                }} 
                aria-label="Remove Food {selectedFood}">−</button>Food: {selectedFood} Price: {prices[index]}<br />
        {/each}
    <button type="button" on:click={() => { 
        if (!wipPrice || wipPrice < 0) {
            errorMsg = "Food must have a non-negative price";
        } else if (wipFood && wipPrice) {
            if (wipFood in selectedFoods) {
                errorMsg = "Duplicate Food name"
            } else {
                selectedFoods = selectedFoods.concat(wipFood); 
                prices = prices.concat(wipPrice);
                foods = foods.filter(food => food !== wipFood);
                wipFood = foods[0];
                wipPrice = null;
                errorMsg = null;
            }
        }
        }} aria-label="Add Food {wipFood}">+</button>
    <select bind:value = {wipFood}>
		{#each foods as food}
			<option value={food}>
				{food}
			</option>
		{/each}
	</select>
    <input type="number" min="0" step="1" bind:value={wipPrice} /><br />
    <button type="submit">Create</button>
    {#if errorMsg}
        <p class="error">{errorMsg}</p>
    {/if}
</form>

<h3>{selectedStaffs}</h3>
<a href={$url('../manage-food-truck')}>Back</a>

<style>
    .error {
        color: red;
    }
</style>
