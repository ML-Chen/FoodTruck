<!-- Screen 15:  Manager Summary Detail -->

<script>
    import { onMount } from 'svelte';
    import { token, userType, storeUsername } from '../_store.js';
    import { Router, url, goto } from '@sveltech/routify';
    import selectedFoodTruck from './food-truck-summary.svelte';
    import axios from 'axios';

    token.useLocalStorage();
    userType.useLocalStorage();
    storeUsername.useLocalStorage();

    // Data fetched from the database
    let orders;

    //props
    // Form values
    let managerUsername = $storeUsername
    let foodTruckName = 'NachoBizness'; //TO DO: GET PROPS WORKING
    let errorMsg;
    let errorMsg2;
    /** @type {{ foodTruckName: string, stationName: string }} */
    // name of the selected foodTruck in the table

    onMount(fetchOrders);

    async function fetchOrders() {
        try {
            const json = (await axios.get('http://localhost:4000/mn_summary_detail', {
                params: { managerUsername, foodTruckName, errorMsg, token: $token }
            })).data;
            console.log(json);
            if (json.error) {
                errorMsg = json.error
            } else {
                /** @type {[{foodTruckName: string, stationName: string, order: int, foodTruckNames: string}]} */
                orders = json.filter(station => Object.keys(station).length !== 0);
            }
            errorMsg = null;
            errorMsg2 = null;
        } catch (error) {
            console.log(error.response.data);
            errorMsg = error.response.data.error;
        }
    }

</script>

<svelte:head>
    <title>Food Truck Summary</title>
</svelte:head>


<h1>Food Truck Detail</h1>
<h3>Food Truck Name: {foodTruckName}</h3>

<table>
    <thead>
        <tr>
            <td>Date</td>
            <td>Customer</td>
            <td>Total Purchase</td>
            <td># Orders</td>
            <td>Foods</td>
        </tr>
    </thead>
    <tbody>
        {#if orders}
            {#each orders as order}
            <tr>
                <td>{order.date}</td>
                <td>{order.customerName}</td>
                <td>{order.totalPurchase}</td>
                <td>{order.orderCount}</td>
                <td>{order.foodNames}</td>
            </tr>
                
            {/each}
        {/if}
    </tbody>
</table>
{#if errorMsg2}
    <p class="error">{errorMsg2}</p>
{/if}

<a href={$url('../../home')}>Back</a>

<style>
    .error {
        color: red;
    }
</style>