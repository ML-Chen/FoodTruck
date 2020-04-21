<!-- Screen #7: Admin Create Station -->

<script>
    import { url, goto } from '@sveltech/routify';
    import { token, userType } from '../_store.js';
    import { onMount } from 'svelte';
    import axios from 'axios';
    token.useLocalStorage();
    userType.useLocalStorage();
    let stationName;
    let capacity;
    let buildingNames = [];
    let selectedBuildingName;
    let errorMsg;
    
    onMount(async () => {
        await fetchBuildings();
    });
    
    async function createStation() {
        if (!stationName) {
            errorMsg = 'Station name must not be blank';
        } else if (!capacity) {
            errorMsg = 'Capacity must not be blank';
        } else if (!selectedBuildingName) {
            errorMsg = 'You must select a building';
        } else {
            try {
                await axios.post('http://localhost:4000/ad_create_station', { stationName, buildingName: selectedBuildingName, capacity, token: $token });
                errorMsg = null;
            } catch (error) {
                console.log(error.response.data)
                errorMsg = error.response.data.error;
            }
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
</script>

<svelte:head>Create Station</svelte:head>

<h1>Create Station</h1>

<form on:submit|preventDefault={createStation}>
    <label for="stationName">Name</label>
    <input type="text" id="stationName" name="stationName" bind:value={stationName} />

    <label for="capacity">Capacity</label>
    <input type="number" min="1" step="1" id="capacity" name="capacity" bind:value={capacity} />

    <label for="building">Sponsor Building</label>
    <select id="building-name" name="building-name" bind:value={selectedBuildingName}>
        {#each [null].concat(buildingNames) as bName}
            <option value={bName} selected={bName === selectedBuildingName}>{bName || ''}</option>
        {/each}
    </select>
    <br />
    <button type="submit">Create</button>
</form>

{#if errorMsg}
    <p class="error">{errorMsg}</p>
{/if}
  
<a href={$url('../manage-building-station')}>Back</a>

<style>
    .error {
        color: red;
    }
</style>