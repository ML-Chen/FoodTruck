<!-- Screen 4: Admin Manage Building & Station -->

<script>
    import { onMount } from 'svelte';
    import { token, userType } from '../_store.js';
    import { url, goto } from '@sveltech/routify';
    import axios from 'axios';

    token.useLocalStorage();
    userType.useLocalStorage();

    // Data fetched from the database
    let buildings;

    // Form values
    let buildingName;
    let stationName;
    let buildingTag;
    let minCapacity;
    let maxCapacity;
    let errorMsg;
    let selectedBuilding; // name of the selected building in the table

    onMount(async () => {
        try {
            const response = await fetch(`http://localhost:4000/ad_filter_building_station?token=${$token}`, { method: 'GET' });
            /** @type {[{buildingName: string, tags: string, stationName: string, capacity: int, foodTruckNames: string}]} */
            buildings = await response.json();
            buildings = buildings.filter(building => Object.keys(building).length !== 0)
        } catch (error) {
            console.log(error);
            errorMsg = 'Network error. Maybe the server is down?';
        }
    });

    export async function handleFilter() {
        try {
            const json = (await axios.get(`http://localhost:4000/ad_filter_building_station`, {
                params: { buildingName, stationName, buildingTag, minCapacity, maxCapacity, errorMsg, selectedBuilding, token: $token }
            })).data;
            if (json.error) {
                errorMsg = json.error
            } else {
                buildings = json.filter(building => Object.keys(building).length !== 0);
            }
        } catch (error) {
            console.log(error);
            errorMsg = 'Network error. Maybe the server is down?';
        }
    }
</script>

<svelte:head>
    <title>Manage Building & Station</title>
</svelte:head>


<h1>Manage Building & Station</h1>

<form on:submit|preventDefault={handleFilter}>
    <label for="username">Building name:</label>
    <select id="building-name" name="station-name" bind:value={buildingName}>
        {#if buildings}
            {#each buildings.map(building => building.buildingName) as bName}
                <option value={bName}>{bName}</option>
            {/each}
        {/if}
    </select>

    <label for="building-tag">Building tag (contain):</label>
    <input type="text" id="building-tag" name="building-tag" bind:value={buildingTag} />

    <label for="station-name">Station name:</label>
    <select id="building-name" name="station-name" bind:value={stationName}>
        {#if buildings}
            {#each Array.from(new Set(buildings.map(building => building.stationName))) as sName}
                <option value={sName}>{sName}</option>
            {/each}
        {/if}
    </select>

    <label for="station-name">Station capacity:</label>
    <input type="number" id="min-capacity" name="min-capacity" bind:value={minCapacity} aria-label="minimum station capacity" />
    <input type="number" id="max-capacity" name="max-capacity" bind:value={maxCapacity} aria-label="maximum station capacity" />

    <br>
    <button type="submit">Filter</button>
    {#if errorMsg}
        <p class="error">{errorMsg}</p>
    {/if}
</form>

<table>
    <thead>
        <tr>
            <td>Building</td>
            <td>Tags</td>
            <td>Station</td>
            <td>Capacity</td>
            <td>Food Trucks</td>
        </tr>
    </thead>
    <tbody>
            {#if buildings}
                {#each buildings as building}
                    <td>
                        <label><input type="radio" bind:group={buildingName} value={building.buildingName}/></label>
                        {building.buildingName}
                    </td>
                    <td>{building.tags}</td>
                    <td>{building.stationName}</td>
                    <td>{building.capacity}</td>
                    <td>{building.foodTruckNames}</td>
                {/each}
            {/if}
    </tbody>
</table>

<a href={$url('../../home')}>Back</a>

<!-- TODO -->
<button>Create building</button>
<button>Update building</button>
<button>Delete building</button>

<button>Create station</button>
<button>Update station</button>
<button>Delete station</button>

<style>
    .error {
        color: red;
    }
</style>