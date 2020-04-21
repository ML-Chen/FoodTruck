<!-- Screen #19 Customer Order History -->

<script>
    import { onMount } from 'svelte';
    import { token, userType, storeUsername } from '../_store.js';
    import { url, goto } from '@sveltech/routify';
    import axios from 'axios';
    token.useLocalStorage();
    userType.useLocalStorage();
    storeUsername.useLocalStorage();
    // Data fetched from the database
    let date;
    let orders = [];
    // Form values
    let errorMsg;
    onMount(async () => {
        await fetchOrders();
    });
    async function fetchOrders() {
        try {
            const orders = (await axios.get('http://localhost:4000/cus_order', {
                params: { customerUsername: $storeUsername, token: $token }
            })).data;
            errorMsg = null;
        } catch (error) {
            console.log(error.response.data);
            errorMsg = error.response.data.error;
        }
    }
  
</script>


<svelte:head>
    <title>Order History</title>
</svelte:head>


<h1>Order History</h1>

<table>
    <thead>
        <tr>
            <td>Date</td>
            <td>OrderID</td>
            <td>Order Total</td>
            <td>Food(s)</td>
            <td>Food Quantity</td>
        </tr>
    </thead>
    <tbody>
        {#each orders as order}
            <tr>
                <td>{order.date}</td>
                <td>{order.orderID}</td>
                <td>{order.orderTotal}</td>
                <td>{order.foods}</td>
                <td>{order.foodQuantity}</td>
            </tr>
        {/each}
    </tbody>
</table>
{#if errorMsg}
    <p class="error">{errorMsg}</p>
{/if}

<a href={$url('../../home')}>Back</a>

<style>
    .error {
        color: red;
    }
</style>
