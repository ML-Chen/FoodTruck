<!-- Screen #8: Admin Update Station -->

<script>
    import { onMount } from 'svelte';
    import { url, goto } from '@sveltech/routify';
    import { token, userType } from '../../_store.js';
    import axios from 'axios';
    token.useLocalStorage();
    userType.useLocalStorage();
    export let stationName;
    const oldStationName = decodeURIComponent(stationName);
    let newStationName = oldStationName;
    let capacity;
    let selectedBuildingName;
    let oldBuildingName = decodeURIComponent(buildingName);
    let newBuildingName = oldBuildingname;
    let errorMsg;
    onMount(async () => {
        await fetchStation();
        await fetchBuilding();
    });
    async function fetchStation() {
        try {
            const json = (await axios.get('http://localhost:4000/ad_view_station_general', {
                params: { stationName: oldStationName, token: $token }
            })).data;
            if (json.error) {
                errorMsg = json.error
            } else {
                newStationName = json.stationName;
                capacity = json.capacity;
                errorMsg = null;
            }
        } catch (error) {
            console.log(error);
            errorMsg = error;
        }
    }
    async function fetchBuilding() {
        try {
            const json = (await axios.get('http://localhost:4000/ad_view_station_building', {
                params: { buildingName: oldBuildingName, token: $token }
            })).data;
            if (json.error) {
                errorMsg = json.error
            } else {
                newBuildingName = json.buildingName;
                capacity = json.capacity;
                errorMsg = null;
            }
        } catch (error) {
            console.log(error);
            errorMsg = error;
        }
    }
    async function updateStation() {
        try {
            const json = (await axios.post('http://localhost:4000/ad_update_station', { oldStationName, newStationName, capacity, token: $token })).data;
                if (json.error) {
                    errorMsg = json.error;
                }
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
    <input type="text" id="stationName" name="stationName" bind:value={newStationName} />

    <label for="capacity">Capacity</label>
    <textarea id="capacity" name="capacity" bind:value={capacity} />

    <label for="building">Building Name:</label>
    <select id="building-name" name="station-name" bind:value={selectedBuildingName}>
        {#if buildings}
            {#each [null].concat(buildings.map(building => building.buildingName)) as bName}
                <option value={bName} selected={bName === selctedBuildingName}>{bName || ''}</option>
            {/each}
        {/if}
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
