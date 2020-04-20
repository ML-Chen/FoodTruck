<!-- Screen 17: Customer Current Information -->

<script>
    import { onMount } from 'svelte';
    import { token, userType, storeUsername } from '../_store.js';
    import { url, goto } from '@sveltech/routify';
    import axios from 'axios';

    token.useLocalStorage();
    userType.useLocalStorage();
    storeUsername.useLocalStorage();

    // Data fetched from the database
    let foodTrucks;
    let stationName;
    let buildingName;
    let tags;
    let description;
    let balance;

    // Form values
    let errorMsg;
    let errorMsg2;
    let selectedTruck; // name of the selected foodTruck in the table

    onMount(async () => {
        fetchCustomerInfo();
        fetchTrucks();
    });

    async function fetchTrucks() {
        try {
            const json = (await axios.get('http://localhost:4000/cus_current_information_foodTruck', {
                params: { customerUsername: $storeUsername, token: $token }
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

    async function fetchCustomerInfo() {
        try {
            const json = (await axios.get('http://localhost:4000/cus_current_information_basic', {
                params: { customerUsername: $storeUsername, token: $token }
            })).data;
            if (json.error) {
                errorMsg = json.error
            } else {
                /** @type {[{stationName: string, buildingName: string, tags: string, description: string, balance: float}]} */
                ({ stationName, buildingName, tags, description, balance } = json);
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

<p>Station: {stationName}</p>
<p>Building: {buildingName}</p>
<p>Building tags: {tags}</p>
<p>Building description: {description}</p>
<p>Balance: {balance}</p>

<table>
    <thead>
        <tr>
            <td>Food Truck</td>
            <td>Manager</td>
            <td>Food(s)</td>
        </tr>
    </thead>
    <tbody>
        {#if foodTrucks}
            {#each foodTrucks as foodTruck}
                <td>
                    <label>
                        <input type="radio" value={foodTruck} bind:group={selectedTruck} />
                    </label>
                    {foodTruck.foodTruckName}
                </td>
                <td>{foodTruck.managerName}</td>
                <td>{foodTruck.foodNames}</td>
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
