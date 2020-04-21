<!-- Screen 11: Manager Manage Food Truck -->

<script>
    import { onMount } from 'svelte';
    import { token, userType, storeUsername } from '../_store.js';
    import { url, goto } from '@sveltech/routify';
    import axios from 'axios';

    token.useLocalStorage();
    userType.useLocalStorage();
    storeUsername.useLocalStorage();

    // Data fetched from the database
    let foodTrucks = [];

    // Form values
    console.log($storeUsername)
    let managerUsername = $storeUsername
    let foodTruckName = null;
    let stationName = null;
    let minStaffCount;
    let maxStaffCount;
    let hasRemainingCapacity = false;
    let errorMsg;
    let errorMsg2;
    let selectedFoodTruck; // name of the selected foodTruck in the table

    onMount(fetchFoodTrucks);

    async function fetchFoodTrucks() {
        try {
            foodTrucks = (await axios.get('http://localhost:4000/mn_filter_foodTruck', {
                params: { managerUsername, foodTruckName, stationName, minStaffCount, maxStaffCount, hasRemainingCapacity, token: $token }
            })).data;
            if (foodTrucks.length == 0) {
                foodTruckName = stationName = null;
            }
            errorMsg = null;
            errorMsg2 = null;
        } catch (error) {
            console.log(error.response.data)
            errorMsg = error.response.data.error;
        }
    }

    async function deleteFoodTruck() {
        console.log(selectedFoodTruck)
        try {
            const response = await axios.post('http://localhost:4000/mn_delete_foodTruck', {
                foodTruckName: selectedFoodTruck, token: $token
            });
            await fetchFoodTrucks();
            errorMsg = null;
            errorMsg2 = null;
        } catch (error) {
            console.log(error.response.data);
            if (error.response.data.error.includes('IntegrityError')) {
                errorMsg2 = "Can't delete Food Truck because something depends on it"
            } else {
                errorMsg2 = 'Network error. Maybe the server is down?';
            }
        }
    }

    $: console.log('foodtruckname ' + JSON.stringify(foodTruckName))
    $: console.log('foodtrucks ' + JSON.stringify(foodTrucks))

</script>

<svelte:head>
    <title>Manage Food Truck</title>
</svelte:head>


<h1>Manage Food Truck</h1>

<form on:submit|preventDefault={fetchFoodTrucks}>
    <label for="username">Food Truck name:</label>
    <select id="foodTruck-name" name="station-name" bind:value={foodTruckName}>
        {#each [null].concat(foodTrucks.map(foodTruck => foodTruck.foodTruckName)) as fName}
            <option value={fName} selected={fName === foodTruckName}>{fName || ''}</option>
        {/each}
    </select>

    <label for="station-name">Station name:</label>
    <select id="foodTruck-name" name="station-name" bind:value={stationName}>
        {#if foodTrucks}
            {#each [null].concat(Array.from(new Set(foodTrucks.map(foodTruck => foodTruck.stationName)))) as sName}
                <option value={sName} selected={sName === stationName}>{sName || ''}</option>
            {/each}
        {/if}
    </select>

    <label>
        Staff Count:
        <input type="number" id="min-capacity" name="min-capacity" bind:value={minStaffCount} aria-label="minimum staff count" />
        –
        <input type="number" id="max-capacity" name="max-capacity" bind:value={maxStaffCount} aria-label="maximum staff count" />
    </label>

    <label for="has-rem-capacity">
        <input type="checkbox" id="has-rem-capacity" bind:checked={hasRemainingCapacity} />
        Has remaining capacity
    </label>

    <br>
    <button type="submit">Filter</button>
    {#if errorMsg}
        <p class="error">{errorMsg}</p>
    {/if}
</form>

<table>
    <thead>
        <tr>
            <td>Food Truck Name</td>
            <td>Station Name</td>
            <td>Remaining Capacity</td>
            <td>Staff(s)</td>
            <td>#Menu Item</td>
        </tr>
    </thead>
    <tbody>
        {#if foodTrucks}
            {#each foodTrucks as foodTruck}
                <tr>
                    <td>
                        <label>
                            <input type="radio" bind:group={selectedFoodTruck} value={foodTruck.foodTruckName}/>
                            {foodTruck.foodTruckName}
                        </label>
                    </td>
                    <td>{foodTruck.stationName}</td>
                    <td>{foodTruck.remainingCapacity}</td>
                    <td>{foodTruck.staffCount}</td>
                    <td>{foodTruck.menuItemCount}</td>
                </tr>
            {/each}
        {/if}
    </tbody>
</table>
{#if errorMsg2}
    <p class="error">{errorMsg2}</p>
{/if}

<a href={$url('../../home')}>Back</a>

<a href={$url('../create-food-truck')}>Create</a>
<a href={$url(`../update-food-truck/${selectedFoodTruck}`)}>Update</a>
<button on:click={deleteFoodTruck}>Delete</button>

<style>
    .error {
        color: red;
    }
</style>
