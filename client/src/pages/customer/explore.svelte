<!-- Screen 16: Customer Explore -->

<script>
    import { onMount } from 'svelte';
    import { token, userType, storeUsername } from '../_store.js';
    import { url, goto } from '@sveltech/routify';
    import axios from 'axios';

    token.useLocalStorage();
    userType.useLocalStorage();
    storeUsername.useLocalStorage();
    
     // Data fetched from the database
    let buildings;

    // Form values
    let buildingName = null;
    let stationName = null;
    let buildingTag;
    let foodTruckName;
    let foodName;
    let errorMsg;
    let errorMsg2;
    /** @type {{ buildingName: string, stationName: string }} */
    let selectedBuilding; // name of the selected building in the table
    
    onMount(fetchBuildings);

    async function fetchBuildings() {
      try {
            buildings = (await axios.get('http://localhost:4000/cus_filter_explore', {
                params: { buildingName, stationName, buildingTag, foodTruckName, foodName, token: $token }
            })).data;
            if (buildings.length === 0) {
                buildingName = null;
                stationName = null;
            }
            errorMsg = null;
            errorMsg2 = null;
        } catch (error) {
            console.log(error.response.data)
            errorMsg = error.response.data.error;
        }
    }

    async function selectLocation() {
        console.log(selectedBuilding)
        try {
            const response = await axios.post('http://localhost:4000/cus_select_location', {
                customerUsername: $storeUsername,
                stationName: selectedBuilding.stationName, token: $token
            });
            errorMsg = null;
            errorMsg2 = null;
        } catch (error) {
            console.log(error.response.data)
            errorMsg = error.response.data.error;
        }
    }

</script>

<svelte:head>
    <title>Explore</title>
</svelte:head>


<h1>Explore</h1>

<form on:submit|preventDefault={fetchBuildings}>
    <label for="username">Building Name:</label>
    <select id="building-name" name="station-name" bind:value={buildingName}>
        {#if buildings}
            {#each [null].concat(buildings.map(building => building.buildingName)) as bName}
                <option value={bName} selected={bName === buildingName}>{bName || ''}</option>
            {/each}
        {/if}
    </select>

    <label for="station-name">Station Name:</label>
    <select id="building-name" name="station-name" bind:value={stationName}>
        {#if buildings}
            {#each [null].concat(Array.from(new Set(buildings.map(building => building.stationName)))) as sName}
                <option value={sName} selected={sName === stationName}>{sName || ''}</option>
            {/each}
        {/if}
    </select>
    
    <label for="building-tag">Building tag (contain):</label>
    <input type="text" id="building-tag" name="building-tag" bind:value={buildingTag} />

    <label for="food-truck-name">Food Truck Name (contain):</label>
    <input type="text" id="food-truck-name" name="food-truck-name" bind:value={foodTruckName} />
    
    <label for="food-name">Food Name (contain):</label>
    <input type="text" id="food-name" name="food-name" bind:value={foodName} />

    <br>
    <button type="submit">Filter</button>
    {#if errorMsg}
        <p class="error">{errorMsg}</p>
    {/if}
</form>

<table>
    <thead>
        <tr>
            <td>Station</td>
            <td>Building</td>
            <td>Food Truck(s)</td>
            <td>Food Name(s)</td>
        </tr>
    </thead>
    <tbody>
        {#if buildings}
            {#each buildings as building}
                <tr>
                    <td>
                        <label>
                            <input type="radio" bind:group={selectedBuilding} value={{ buildingName: building.buildingName, stationName: building.stationName }}/>
                            {building.stationName}
                        </label>
                    </td>
                    <td>{building.buildingName}</td>
                    <td>{building.foodTruckNames}</td>
                    <td>{building.foodNames}</td>
                </tr>
            {/each}
        {/if}
    </tbody>
</table>
{#if errorMsg2}
    <p class="error">{errorMsg2}</p>
{/if}

<a href={$url('../../home')}>Back</a>

<button type="button" on:click={selectLocation}>Select As Current Location</button>

<style>
    .error {
        color: red;
    }
</style>
