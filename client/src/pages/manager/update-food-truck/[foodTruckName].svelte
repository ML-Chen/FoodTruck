<!-- Screen #13 Manager Update Food Truck -->

<script>
    export let foodTruckName;
    foodTruckName = decodeURIComponent(foodTruckName);

    import { onMount } from 'svelte';
    import { url, goto } from '@sveltech/routify';
    import { token, userType, storeUsername } from '../../_store.js';
    import axios from 'axios';

    token.useLocalStorage();
    userType.useLocalStorage();
    storeUsername.useLocalStorage();
    const managerUsername = $storeUsername;

    // Data fetched from the database
    let stations = []; // string[]
    let foods = []; // [[foodName: string, foodPrice: number]]
    let menuItems = [];
    let staffs = []; // [{ staffUsername: string, staffName: string }]
    let availableStaffs = []; // a temporary variable used only to add values to staffs
    let selectedStaffs = []; // fetched from database, later currently selected staffs

    //params
    let selectedStation // string
    let wipFood; // string
    let wipPrice; // number
    let errorMsg; // string[]

    onMount(async () => {
        await fetchAvailableStaffs();
        await fetchSelectedStaffs();
        staffs = selectedStaffs.concat(availableStaffs);
        await fetchMenuItems();
        await callHelpers();
        console.log(availableStaffs);
        console.log(selectedStaffs);
        console.log(menuItems);
    });

    async function fetchAvailableStaffs() {
        try {
            availableStaffs = (await axios.get('http://localhost:4000/mn_view_foodTruck_available_staff', {
                params: { managerUsername, foodTruckName, token: $token }
            })).data;
            errorMsg = null;
        } catch (error) {
            console.log(error);
            errorMsg = error;
        }
    }

    async function fetchSelectedStaffs() {
        try {
            selectedStaffs = (await axios.get('http://localhost:4000/mn_view_foodTruck_staff', {
                params: {foodTruckName, token: $token }
            })).data;
            errorMsg = null;
        } catch (error) {
            console.log(error);
            errorMsg = error;
        }
    }
    async function fetchMenuItems() {
        try {
            menuItems = (await axios.get('http://localhost:4000/mn_view_foodTruck_menu', {
                params: {foodTruckName , token: $token }
            })).data.map(obj => [obj.foodName, obj.price]);
            errorMsg = null;
        } catch (error) {
            console.log(error);
            errorMsg = error;
        }
    }

    async function callHelpers() {
        try {
            const currentStation = (await axios.get('http://localhost:4000/mn_filter_foodTruck', { params: { managerUsername, foodTruckName, token: $token }})).data[0].stationName;
            selectedStation = currentStation;
            const availableStations = (await axios.get('http://localhost:4000/help_create_food_truck', { params: {queryType: 'Station'}})).data.map(station => station.stationName).filter(stationName => stationName !== currentStation);
            stations = [currentStation].concat(availableStations);
            foods = (await axios.get('http://localhost:4000/help_create_food_truck', { params: {queryType: 'Food'}})).data;
        } catch (error) {
            console.log(error)
            errorMsg = error.response.data.error;
        }
    }
    async function updatefoodTruck() {
        if (!foodTruckName) {
            errorMsg = 'foodTruck name must not be blank';
        } else if (!selectedStation) {
            errorMsg = 'Please select a station';
        } else if (!selectedStaffs) {
            errorMsg = 'Please assign at least one staff';
        } else if (menuItems == []) {
            errorMsg = 'Please add at least one food'; 
        } else {
            try {
                const json = (await axios.post('http://localhost:4000/mn_update_foodTruck_station', { foodTruckName, stationName: selectedStation, managerUsername, token: $token })).data;
                // TODO: This just sets the prices of existing items. Enable adding and removing menu items.
                for (let i = 0; i < menuItems.length; i++) {
                    console.log(menuItems[i]);
                    await axios.post('http://localhost:4000/mn_update_foodTruck_MenuItem', { foodTruckName, foodName: menuItems[i][0], price: menuItems[i][1], managerUsername, token: $token })
                }
                for (const selectedStaff of selectedStaffs) {
                    await axios.post('http://localhost:4000/mn_update_foodTruck_staff', { foodTruckName, staffName: selectedStaff.staffUsername, managerUsername, token: $token })
                }
                const unselectedStaffs = staffs.filter(staff => !(staff in selectedStaffs));
                for (const unselectedStaff of unselectedStaffs) {
                    console.log(unselectedStaff.staffUsername);
                    await axios.post('http://localhost:4000/mn_update_foodTruck_remove_staff', { foodTruckName, staffName: unselectedStaff.staffUsername, token: $token })
                }
                $goto(`../${foodTruckName}`);
                    
            } catch (error) {
                console.log(error);
                errorMsg = error.response;
            }
        }
    }
</script>

<svelte:head>Update Food Truck</svelte:head>

<h1>Update Food Truck</h1>

<form on:submit|preventDefault={updatefoodTruck}>
    <label for="foodTruckName">Name</label>
    <input type="text" id="foodTruckName" name="foodTruckName" bind:value={foodTruckName} />

    <select id="station-name" name="station-name" bind:value={selectedStation}>
        {#each stations as sName}
            <option value={sName}>{sName}</option>
        {/each}
    </select>
    <label for="selectedStaffs">Assign Staffs:</label>
 
    <select multiple bind:value={selectedStaffs}>
        {#each staffs as staff}
            <option value={staff} selected="selected">
                {staff.staffName}
            </option>
        {/each}
    </select>
   
    <label for="menuItems">Menu Item</label>
        {#each menuItems as menuItem, index (menuItem)}
            <button type="button" on:click={() => { 
                menuItems = menuItems.filter((_, i) => i !== index)
                }} 
                aria-label="Remove Food {menuItem[0]}">−</button>Food: {menuItem[0]} Price: {menuItem[1]}<br />
        {/each}
    <button type="button" on:click={() => { 
        if (wipFood && wipPrice) {
            if (wipFood in menuItems) {
                errorMsg = "Duplicate Food name"
            } else {
                menuItems = menuItems.concat([[wipFood, wipPrice]]); 
                wipFood = '';
                wipPrice = 0;
                }
            }
        }} aria-label="Add Food {wipFood}">+</button>
    <select bind:value = {wipFood}>
		{#each foods as food}
			<option value={food.foodName}>
				{food.foodName}
			</option>
		{/each}
	</select>
    <input type="number" bind:value={wipPrice} /><br />
    <button type="submit">Update</button>
    {#if errorMsg}
        <p>{errorMsg}</p>
    {/if}
</form>

<a href={$url('../../manage-food-truck')}>Back</a>