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
    let errorMsg2;
    /** @type {{ buildingName: string, stationName: string }} */
    let selectedBuilding; // name of the selected building in the table

    onMount(fetchBuildings);

    async function fetchBuildings() {
        try {
            const json = (await axios.get('http://localhost:4000/ad_filter_building_station', {
                params: { buildingName, stationName, buildingTag, minCapacity, maxCapacity, errorMsg, selectedBuilding, token: $token }
            })).data;
            if (json.error) {
                errorMsg = json.error
            } else {
                /** @type {[{buildingName: string, tags: string, stationName: string, capacity: int, foodTruckNames: string}]} */
                buildings = json.filter(building => Object.keys(building).length !== 0);
            }
            errorMsg = null;
            errorMsg2 = null;
        } catch (error) {
            console.log(error);
            errorMsg = 'Network error. Maybe the server is down?';
        }
    }

    async function deleteBuilding() {
        console.log(selectedBuilding)
        try {
            const response = await axios.post('http://localhost:4000/ad_delete_building', {
                buildingName: selectedBuilding.buildingName, token: $token
            });
            await fetchBuildings();
            errorMsg = null;
            errorMsg2 = null;
        } catch (error) {
            console.log(error);
            if (error.response.data.error.includes('IntegrityError')) {
                errorMsg2 = "Can't delete building because something depends on it"
            } else {
                errorMsg2 = 'Network error. Maybe the server is down?';
            }
        }
    }

    async function deleteStation() {
        try {
            const response = await axios.post('http://localhost:4000/ad_delete_station', {
                stationName: selectedBuilding.stationName, token: $token
            });
            await fetchBuildings();
            errorMsg = null;
            errorMsg2 = null;
        } catch (error) {
            console.log(error);
            if (error.response.data.error.includes('IntegrityError')) {
                errorMsg2 = "Can't delete station because something depends on it"
            } else {
                errorMsg2 = 'Network error. Maybe the server is down?';
            }
        }
    }
</script>

<svelte:head>
    <title>Manage Building & Station</title>
</svelte:head>


<h1>Manage Building & Station</h1>

<form on:submit|preventDefault={fetchBuildings}>
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
                        <label>
                            <input type="radio" bind:group={selectedBuilding} value={{ buildingName: building.buildingName, stationName: building.stationName }}/>
                        </label>
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
{#if errorMsg2}
    <p class="error">{errorMsg2}</p>
{/if}

<a href={$url('../../home')}>Back</a>

<a href={$url('../create-building')}>Create building</a>
<a href={$url('../update-building')} scoped={{selectedBuilding}}>Update building</a>
<button on:click={deleteBuilding}>Delete building</button>

<a href={$url('../create-station')}>Create station</a>
<a href={$url('../update-station')} scoped={{selectedBuilding}}>Update station</a>
<button on:click={deleteStation}>Delete station</button>

<style>
    .error {
        color: red;
    }
</style>