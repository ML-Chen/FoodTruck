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
    let foods = [];

    let foodTruckName;
    let selectedStation;
    let selectedStaffs;
    let selectedFoods = [];
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
                const foodsJson = (await axios.get('http://localhost:4000/help_create_food_truck', { params: {queryType: 'Food'}})).data;
                if (stationsJson.error || staffsJson.error) {
                    errorMsg = stationsJson.error;
                } else {
                    stations = stationsJson.filter(station => Object.keys(station).length !== 0);
                    staffs = staffsJson.filter(staff => Object.keys(staff).length !== 0);
                    foods = foodsJson.filter(food => Object.keys(food).length !== 0);
                    selectedStation = stations.length > 0 ? stations[0].stationName : null;
                    wipFoods = stations.length > 0 ? foods[0].foodName : null;
                    console.log(stations)
                    console.log(staffs)
                    console.log(foods)
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
        } else if (selectedFoods == []) {
            errorMsg = 'Please add at least one food'; 
        } else {
            try {
                const json = (await axios.post('http://localhost:4000/mn_create_foodTruck_add_station', { foodTruckName, stationName: selectedStation, managerUsername: $storeUsername, token: $token })).data;    
                for (let i = 0; i < selectedFoods.length; i++) {
                    console.log(selectedFoods[i]);
                    console.log(prices[i]);
                    axios.post('http://localhost:4000/mn_create_foodTruck_add_MenuItem', { foodTruckName, foodName: selectedFoods[i], price: prices[i], managerUsername: $storeUsername, token: $token })
                }
                for (let i = 0; i < selectedStaffs.length; i++) {
                    console.log(selectedStaffs[i]);
                    axios.post('http://localhost:4000/mn_create_foodTruck_staff', { foodTruckName, staffName: selectedStaff[i], managerUsername: $storeUsername, token: $token })
                }
                foodTruckName = description = wipFoods = errorMsg = '';
                selectedFoods = [];
                    
            } catch (error) {
                console.log(error);
                errorMsg = error.response.data.error;
            }
        }
    }
</script>

<svelte:head>Update Food Truck</svelte:head>

<h1>Update Food Truck</h1>

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


   
    <label for="selectedFoods">Menu Item (name and price)</label>
        {#each selectedFoods as selectedFood, index (selectedFood)}
            <button type="button" on:click={() => { 
                selectedFoods = selectedFoods.filter((_, i) => i !== index)
                prices = prices.filter((_, i) => i !== index)
                }} 
                aria-label="Remove Food {selectedFood}">−</button>Food: {selectedFood} Price: {prices[index]}<br />
        {/each}
    <button type="button" on:click={() => { 
        if (wipFoods && wipPrices) {
            if (wipFoods in selectedFoods) {
                errorMsg = "Duplicate Food name"
            } else {
                selectedFoods = selectedFoods.concat(wipFoods); 
                prices = prices.concat(wipPrices);
                wipFoods='';
                wipPrices= 0;
                } 
            }
        }} aria-label="Add Food {wipFoods}">+</button>
    <select bind:value = {wipFoods}>
		{#each foods as food}
			<option value={food.foodName}>
				{food.foodName}
			</option>
		{/each}
	</select>
    <input type="number" min="0" step="1" bind:value={wipPrices} /><br />
    <button type="submit">Create</button>
    {#if errorMsg}
        <p class="error">{errorMsg}</p>
    {/if}
    <h1>{selectedStaffs}</h1>
    <h1>{selectedStation}</h1>
</form>

<a href={$url('../../home')}>Back</a>

<style>
    .error {
        color: red;
    }
</style>