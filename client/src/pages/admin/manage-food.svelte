<!-- Screen 4: Admin Manage Building & Station -->

<script>
    import { onMount } from 'svelte';
    import { token, userType } from '../_store.js';
    import { url, goto } from '@sveltech/routify';
    import axios from 'axios';

    token.useLocalStorage();
    userType.useLocalStorage();

    // Data fetched from the database
    let foods;

    // Form values
    let foodName;
    let MenuCount;
    let errorMsg;
    let errorMsg2;
    /** @type {{ buildingName: string, stationName: string }} */
    let selectedFood; // name of the selected building in the table

    onMount(fetchFoods);

    async function fetchFoods() {
        try {
            const json = (await axios.get('http://localhost:4000/ad_filter_food', {
                params: { foodName, MenuCount, errorMsg, selectedFood, token: $token }
            })).data;
            if (json.error) {
                errorMsg = json.error
            } else {
                /** @type {[{buildingName: string, tags: string, stationName: string, capacity: int, foodTruckNames: string}]} */
                foods = json.filter(food => Object.keys(food).length !== 0);
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
    <title>Manage Food</title>
</svelte:head>


<h1>Manage Food</h1>

<form on:submit|preventDefault={createFood}>
    <label for="FoodName">Name</label>
    <input type="text" id="FoodName" name="FoodName" bind:value={FoodName} />
    </select>



    <br>
    <button type="submit">Filter</button>
    {#if errorMsg}
        <p class="error">{errorMsg}</p>
    {/if}
</form>

<table>
    <thead>
        <tr>
            <td>Name</td>
            <td>Menu Count</td>
            <td>Purchase Count</td>
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