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

    // Tablesort
    import {TableSort} from 'svelte-tablesort'

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
    let selectedFoodTruck = { foodTruckName: null, stationName: null }

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
            console.log(error.response.data)
            errorMsg = error.response.data.error;
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

<!-- TODO: make columns sortable with https://github.com/mattiash/svelte-tablesort -->

<!-- <TableSort items={items}>
	<tr slot="thead">
		<th data-sort="title">Title</th>
		<th data-sort="user">User</th>
	</tr>
	<tr slot="tbody" let:item={item}>
		<td><a href="{item.url}">{item.title}</a></td>
		<td>{item.user}</td>
	</tr>
    </TableSort>  -->

<TableSort items={items}>
    <tr slot="thead">
        <th data-sort="food-truck">Food Truck</th>
        <th data-sort="total-order">Total Order</th>
        <th data-sort="total-revenue">Total Revenue</th>
        <th data-sort="#customer"># Customer</th>
    </tr>
    <tr slot="tbody">
        {#if foodTrucks}
            {#each foodTrucks as foodTruck}
                <tr>
                    <td>
                        <label>
                            <a href="input type="radio" bind:group={selectedFoodTruck} value={{ foodTruckName: foodTruck.foodTruckName, stationName: foodTruck.stationName }}"
                               >{foodTruckName: foodTruck.foodTruckName}</a>
                        </label>
                    </td>
                    <td><a href="{foodTruck.totalOrder}">{foodTruck.totalOrder}</a></td>
                    <td><a href="{foodTruck.totalRevenue}">{foodTruck.totalRevenue}</a></td>
                    <td><a href="{foodTruck.totalCustomer}">{foodTruck.totalCustomer}</a></td>
                </tr>
            {/each}
        {/if}
    </tr>
</table>
{#if errorMsg2}
    <p class="error">{errorMsg2}</p>
{/if}

<a href={$url('../../home')}>Back</a>
<a href={$url(`../summary-detail/${selectedFoodTruck['foodTruckName']}`)}>Detail</a>
<style>
    .error {
        color: red;
    }
</style>
