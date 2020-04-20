<!-- Screen 17: Customer Current Information -->

<script>
    import { onMount } from 'svelte';
    import { token, userType } from '../_store.js';
    import { url, goto } from '@sveltech/routify';
    import axios from 'axios';

    token.useLocalStorage();
    userType.useLocalStorage();

    // Data fetched from the database
    let customers;

    // Form values
    let customerUsername;
    let errorMsg;
    let errorMsg2;
    /** @type {{ customerUsername: string }} */
    let selectedTruck; // name of the selected foodTruck in the table

    onMount(fetchTrucks);

    async function fetchTrucks() {
        try {
            const json = (await axios.get('http://localhost:4000/ad_filter_building_station', {
                params: { customerUsername, token: $token }
            })).data;
            if (json.error) {
                errorMsg = json.error
            } else {
                /** @type {[{foodTruckName: string, managerName: string, foodNames: string}]} */
                foodTrucks = json.filter(foodTruck => Object.keys(foodTruck).length !== 0);
            }
            errorMsg = null;
        } catch (error) {
            console.log(error);
            errorMsg = 'Network error. Maybe the server is down?';
        }
    }

</script>

<svelte:head>
    <title>Current Information</title>
</svelte:head>


<h1>Current Information</h1>

<form on:submit|preventDefault={fetchTrucks}>
    <label for="username">Food Truck</label>
    <select id="food-truck-name" name="food-truck-name" bind:value={foodTruckName}>
        {#if foodTrucks}
            {#each foodTrucks.map(foodTruck => foodTruck.foodTruckName) as fName}
                <option value={fName}>{fName}</option>
            {/each}
        {/if}
    </select>

    <label for="station-name">Station</label>
    <div title={stationName} id="station-name" name="station-name" bind:value={stationName} />

    <label for="building-name">Building</label>
    <div title={buildingName} id="building-name" name="building-name" bind:value={buildingName} />

    <label for="building-tags">Building Tag(s)</label>
    <div title={buildingTags} id="building-tags" name="building-tags" bind:value={buildingTags} />
    
    <label for="building-description">Building Description</label>
    <div title={buildingDescription} id="building-description" name="building-description" bind:value={buildingDescription} />
    
    <label for="customer-balance">Building Tag(s)</label>
    <div title={customerBalance} id="customer-balance" name="customer-balance" bind:value={customerBalance} />

</form>

<table>
    <thead>
        <tr>
            <td>Food Truck</td>
            <td>Manager</td>
            <td>Food(s)</td>
        </tr>
    </thead>
    <tbody>
            {#if buildings}
                {#each buildings as building}
                    <td>
                        <label>
                            <input type="radio" bind:value={{ foodTruckName: foodTruck.foodTruckName }}/>
                        </label>
                        {foodTruck.foodTruckName}
                    </td>
                    <td>{foodTruck.manager}</td>
                    <td>{foodTruck.food}</td>
                {/each}
            {/if}
    </tbody>
</table>
{#if errorMsg2}
    <p class="error">{errorMsg2}</p>
{/if}

<a href={$url('../../home')}>Back</a>

<a href={$url('../order')}>Order</a>

<style>
    .error {
        color: red;
    }
</style>
