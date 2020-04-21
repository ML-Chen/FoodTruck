<!-- Screen #7: Admin Create Station -->

<script>
    import { url, goto } from '@sveltech/routify';
    import { token, userType } from '../_store.js';
    import axios from 'axios';
    token.useLocalStorage();
    userType.useLocalStorage();
    let stationName;
    let capacity;
    let buildingName;
    let errorMsg;
    
    onMount(async () => {
        await fetchBuilding();
    });
    
    async function createStation() {
        if (!stationName) {
            errorMsg = 'Station name must not be blank';
        } else if (!capacity) {
            errorMsg = 'Capacity must not be blank';
        } else {
            try {
                const json = (await axios.post('http://localhost:4000/ad_create_station', { stationName, capacity, token: $token })).data;
                    if (json.error) {
                        errorMsg = json.error;
                    }
            } catch (error) {
                console.log(error.response.data)
                errorMsg = error.response.data.error;
            }
        }
    }
    async function fetchBuilding() {
        try {
            const json = (await axios.get('http://localhost:4000/ad_view_building_general', {
                params: { buildingName: buildingName, token: $token }
            })).data;
            if (json.error) {
                errorMsg = json.error
            } else {
                buildingName = json.buildingName;
                errorMsg = null;
            }
        } catch (error) {
            console.log(error);
            errorMsg = error;
        }
    }
</script>

<svelte:head>Create Station</svelte:head>

<h1>Create Station</h1>

<form on:submit|preventDefault={createStation}>
    <label for="stationName">Name</label>
    <input type="text" id="stationName" name="stationName" bind:value={stationName} />

    <label for="capacity">Description</label>
    <textarea id="capacity" name="capacity" bind:value={capacity} />

    <label for="building">Sponsored Building</label>
    <select id="building-name" name="building-name" bind:value={buildingName}>
        {#if buildings}
            {#each [null].concat(buildings.map(building => building.buildingName)) as bName}
                <option value={bName} selected={bName === buildingName}>{bName || ''}</option>
            {/each}
        {/if}
    <button type="submit">Create</button>
</form>
  
<a href={$url('../../home')}>Back</a>
