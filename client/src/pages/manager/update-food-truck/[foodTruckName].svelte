<!-- Screen #13 Manager Update Food Truck -->

<script>
    export let foodTruckName;
    const oldTruckName = decodeURIComponent(foodTruckName);
    // TODO; see admin/update-building/[buildingName].svelte for a similar page

    import { onMount } from 'svelte';
    import { url, goto } from '@sveltech/routify';
    import { token, userType, storeUsername } from '../../_store.js';
    import axios from 'axios';

    token.useLocalStorage();
    userType.useLocalStorage();
    storeUsername.useLocalStorage();


    // Data fetched from the database
    let stations = [];
    let availableStaffs = [];
    let foods = [];
    let menuItems = [];
    let selectedStation;
    let selectedStaffs;   

    //params
    let wipFoods;
    let wipPrices;
    let errorMsg;
    let managerUsername = $storeUsername

    onMount(async () => {
        await fetchAvailableStaffs();
        await fetchSelectedStaffs();
        await fetchMenuItems();
        await callHelpers();
        console.log(availableStaffs);
        console.log(selectedStaffs);
        console.log(menuItems);
    });

    async function fetchAvailableStaffs() {
        try {
            const json = (await axios.get('http://localhost:4000/mn_view_foodTruck_available_staff', {
                params: { managerUsername, foodTruckName , token: $token }
            })).data;
            if (json.error) {
                errorMsg = json.error
            } else {
                availableStaffs = json.map(obj => obj.staffName);
                errorMsg = null;
            }
        } catch (error) {
            console.log(error);
            errorMsg = error;
        }
    }

    async function fetchSelectedStaffs() {
        try {
            const json = (await axios.get('http://localhost:4000/mn_view_foodTruck_staff', {
                params: {foodTruckName , token: $token }
            })).data;
            if (json.error) {
                errorMsg = json.error
            } else {
                selectedStaffs = json.map(obj => obj.assignedStaff);
                errorMsg = null;
            }
        } catch (error) {
            console.log(error);
            errorMsg = error;
        }
    }
    async function fetchMenuItems() {
        try {
            const json = (await axios.get('http://localhost:4000/mn_view_foodTruck_menu', {
                params: {foodTruckName , token: $token }
            })).data;
            if (json.error) {
                errorMsg = json.error
            } else {
                menuItems = json.map(obj => [obj.foodName, obj.price]); //array of menu items
                errorMsg = null;
            }
        } catch (error) {
            console.log(error);
            errorMsg = error;
        }
    }

    async function callHelpers() {
            try {
                const stationsJson = (await axios.get('http://localhost:4000/help_create_food_truck', { params: {queryType: 'Station'}})).data;
                const foodsJson = (await axios.get('http://localhost:4000/help_create_food_truck', { params: {queryType: 'Food'}})).data;
                if (stationsJson.error || staffsJson.error) {
                    errorMsg = stationsJson.error;
                } else {
                    stations = stationsJson.filter(station => Object.keys(station).length !== 0);
                    foods = foodsJson.filter(food => Object.keys(food).length !== 0);
                    console.log(stations)
                    console.log(foods)
                }
            } catch (error) {
                console.log(error)
                errorMsg = error;
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
                foodTruckName = description = wipFoods = errorMsg = '';
                selectedFoods = [];
                    
            } catch (error) {
                console.log(error);
                errorMsg = error.response;
            }
        }
    }
</script>

<svelte:head>Create Food Truck</svelte:head>

<h1>Create Food Truck</h1>

<!-- <form on:submit|preventDefault={createfoodTruck}>
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


   
    <label for="selectedFoods">Menu Item</label>
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
    <input type="number" bind:value={wipPrices} /><br />
    <button type="submit">Create</button>
    <p>{errorMsg}</p>
    <h1>{selectedStaffs}</h1>
    <h1>{selectedStation}</h1> -->
<!-- </form> -->

<a href={$url('../../home')}>Back</a>