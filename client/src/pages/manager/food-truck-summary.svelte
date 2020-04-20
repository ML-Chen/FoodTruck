<!-- Screen 4: Admin Manage Food Truck -->

<script>
    import { onMount } from 'svelte';
    import { token, userType, storeUsername } from '../_store.js';
    import { url, goto } from '@sveltech/routify';
    import axios from 'axios';
    import { TableSort } from 'svelte-tablesort';

    token.useLocalStorage();
    userType.useLocalStorage();
    storeUsername.useLocalStorage();

    // Data fetched from the database
    let foodTrucks;
    let stations;

    // Form values
    console.log($storeUsername)
    let managerUsername = $storeUsername
    let foodTruckName;
    let stationName;
    let minDate;
    let maxDate;
    let errorMsg;
    let errorMsg2;
    /** @type {{ foodTruckName: string, stationName: string }} */
    let selectedFoodTruck; // name of the selected foodTruck in the table

    onMount(async () => {
        await fetchStations();
        await fetchFoodTrucks();
    });

    async function fetchStations() {
        try {
            const json = (await axios.get('http://localhost:4000/mn_get_station', {
                params: { managerUsername, errorMsg, token: $token }
            })).data;
            console.log(json);
            if (json.error) {
                errorMsg = json.error
            } else {
                /** @type {[{foodTruckName: string, stationName: string, date: int, foodTruckNames: string}]} */
                stations = json.filter(station => Object.keys(station).length !== 0);
            }
            errorMsg = null;
            errorMsg2 = null;
        } catch (error) {
            console.log(error);
            errorMsg = 'Network error. Maybe the server is down?';
        }
    }

    async function fetchFoodTrucks() {
        try {
            const json = (await axios.get('http://localhost:4000/mn_filter_summary', {
                params: { managerUsername, foodTruckName, stationName, minDate, maxDate, errorMsg, selectedFoodTruck, token: $token }
            })).data;
            console.log(json);
            if (json.error) {
                errorMsg = json.error
            } else {
                /** @type {[{foodTruckName: string, stationName: string, date: int, foodTruckNames: string}]} */
                foodTrucks = json.filter(foodTruck => Object.keys(foodTruck).length !== 0);
            }
            errorMsg = null;
            errorMsg2 = null;
        } catch (error) {
            console.log(error);
            errorMsg = 'Network error. Maybe the server is down?';
        }
    }

</script>

<svelte:head>
    <title>Food Truck Summary</title>
</svelte:head>


<h1>Food Truck Summary</h1>

<form on:submit|preventDefault={fetchFoodTrucks}>
    <label for="food-truck-name">Food Truck name:</label>
    <input type="text" name="food-truck-name" bind:value={foodTruckName}>

    <label for="station-name">Station name:</label>
    <select id="foodTruck-name" name="station-name" bind:value={stationName}>
        {#if stations}
            {#each Array.from(new Set(stations.map(station => station.stationName))) as sName}
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

<!-- TODO: make columns sortable with https://github.com/mattiash/svelte-tablesort -->

<table>
    <thead>
        <tr>
            <td>foodTruck</td>
            <td>Total Order</td>
            <td>Total Revenue</td>
            <td># Customer</td>
        </tr>
    </thead>
    <tbody>
        {#if foodTrucks}
            {#each foodTrucks as foodTruck}
                <td>
                    <label>
                        <input type="radio" bind:group={selectedFoodTruck} value={{ foodTruckName: foodTruck.foodTruckName, stationName: foodTruck.stationName }}/>
                    </label>
                    {foodTruck.foodTruckName}
                </td>
                <td>{foodTruck.totalOrder}</td>
                <td>{foodTruck.totalRevenue}</td>
                <td>{foodTruck.totalCustomer}</td>
            {/each}
        {/if}
    </tbody>
</table>
{#if errorMsg2}
    <p class="error">{errorMsg2}</p>
{/if}

<a href={$url('../../home')}>Back</a>
<a href={$url('../summary-detail')} scoped={{selectedFoodTruck}}>Detail</a>

<style>
    .error {
        color: red;
    }
</style>