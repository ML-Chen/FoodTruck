<!-- Screen 4: Admin Manage Food Truck -->

<script>
    import { onMount } from 'svelte';
    import { token, userType, storeUsername } from '../_store.js';
    import { Router, url, goto } from '@sveltech/routify';
    import axios from 'axios';
    import { TableSort } from 'svelte-tablesort';

    token.useLocalStorage();
    userType.useLocalStorage();
    storeUsername.useLocalStorage();

    // Data fetched from the database
    let foodTrucks = [];
    let stations = [];

    // Form values
    let managerUsername = $storeUsername
    let foodTruckName;
    let stationName;
    let minDate;
    let maxDate;
    let errorMsg;
    let selectedFoodTruck; // name of selected food truck

    onMount(async () => {
        await fetchStations();
        await fetchFoodTrucks();
        errorMsg = null;
    });

    async function fetchStations() {
        try {
            stations = (await axios.get('http://localhost:4000/mn_get_station', {
                params: { managerUsername, token: $token }
            })).data;
        } catch (error) {
            console.log(error.response.data)
            errorMsg = error.response.data.error;
        }
    }

    async function fetchFoodTrucks() {
        try {
            foodTrucks = (await axios.get('http://localhost:4000/mn_filter_summary', {
                params: { managerUsername, foodTruckName, stationName, minDate, maxDate, token: $token }
            })).data;
        } catch (error) {
            console.log(error.response.data)
            errorMsg = error.response.data.error;
        }
    }

</script>

<svelte:head>
    <title>Food Truck Summary</title>
</svelte:head>


<h1>Food Truck Summary</h1>

<form on:submit|preventDefault={fetchFoodTrucks}>
    <label for="food-truck-name">Food Truck Name (contain)</label>
    <input type="text" name="food-truck-name" bind:value={foodTruckName}>

    <label for="station-name">Station name:</label>
    <select id="foodTruck-name" name="station-name" bind:value={stationName}>
        {#if stations}
            {#each stations.map(station => station.stationName) as sName}
                <option value={sName}>{sName}</option>
            {/each}
        {/if}
    </select>
    <br />
    Date:
    <input type="date" id="min-date" name="min-date" bind:value={minDate} aria-label="minimum date" />
    &ndash;
    <input type="date" id="max-date" name="max-date" bind:value={maxDate} aria-label="maximum date" />

    <br>
    <button type="submit">Filter</button>
    {#if errorMsg}
        <p class="error">{errorMsg}</p>
    {/if}
</form>

<TableSort items={foodTrucks}>
    <tr slot="thead">
        <th></th>
        <th data-sort="foodTruckName">Food Truck</th>
        <th data-sort="totalOrder">Total Order</th>
        <th data-sort="totalRevenue">Total Revenue</th>
        <th data-sort="totalCustomer"># Customer</th>
    </tr>
    <tr slot="tbody" let:item={foodTruck}>
        <input type="radio" bind:group={selectedFoodTruck} value={foodTruck.foodTruckName} />
        <td>{foodTruck.foodTruckName}</td>
        <td>{foodTruck.totalOrder}</td>
        <td>{foodTruck.totalRevenue}</td>
        <td>{foodTruck.totalCustomer}</td>
    </tr>
</TableSort>

{#if errorMsg}
    <p class="error">{errorMsg}</p>
{/if}

<a href={$url('../../home')}>Back</a>
<a href={$url(`../summary-detail/${selectedFoodTruck}`)}>Detail</a>
<style>
    .error {
        color: red;
    }
</style>
