<!-- Screen #8: Admin Update Station -->

<script>
    import { onMount } from 'svelte';
    import { url, goto } from '@sveltech/routify';
    import { token, userType } from '../../_store.js';
    import axios from 'axios';
    token.useLocalStorage();
    userType.useLocalStorage();
    export let stationName;
    stationName = decodeURIComponent(stationName);
    let currentBuildingName; // the building the station is currently at
    let selectedBuildingName;
    let buildingNames = []; // available buildings
    let capacity;
    let errorMsg;

    onMount(async () => {
        await fetchStation();
        await fetchBuildings();
    });
    async function fetchStation() {
        try {
            const json = (await axios.get('http://localhost:4000/ad_view_station', {
                params: { stationName, token: $token }
            })).data;
            console.log(json);
            capacity = json.capacity;
            currentBuildingName = json.buildingName;
            selectedBuildingName = currentBuildingName;
            errorMsg = null;
        } catch (error) {
            console.log(error.response.data);
            errorMsg = error.response.data.error;
        }
    }
    async function fetchBuildings() {
        try {
            const json = (await axios.get('http://localhost:4000/ad_get_available_building', {
                params: { token: $token }
            })).data;
            buildingNames = json.map(building => building.buildingName);
            errorMsg = null;
        } catch (error) {
            console.log(error.response.data);
            errorMsg = error.response.data.error;
        }
    }
    async function updateStation() {
        try {
            const json = (await axios.post('http://localhost:4000/ad_update_station', { stationName, capacity, buildingName: selectedBuildingName, token: $token })).data;
        } catch (error) {
            console.log(error.response.data);
            errorMsg = error.response.data.error;
        }
    }
</script>

<svelte:head><title>Update Station</title></svelte:head>

<h1>Update Station</h1>

<form on:submit|preventDefault={updateStation}>
    <label for="stationName">Name</label>
    <input type="text" id="stationName" name="stationName" value={stationName} disabled />

    <label for="capacity">Capacity</label>
    <input type="number" id="capacity" name="capacity" bind:value={capacity} />

    <label for="building">Building Name:</label>
    <select id="building-name" name="station-name" bind:value={selectedBuildingName}>
        {#each [currentBuildingName].concat(buildingNames) as bName}
            <option value={bName} selected={bName === selectedBuildingName}>{bName || ''}</option>
        {/each}
    </select>
  
    <button type="submit">Update</button>
</form>

{#if errorMsg}
    <p class="errorMsg">{errorMsg}</p>
{/if}

<a href={$url('../../manage-building-station')}>Back</a>

<style>
    .errorMsg {
        color: red;
    }
</style>
