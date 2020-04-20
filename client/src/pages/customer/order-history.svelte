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
    let orderID;
    let orderTotal;
    let foodNames;
    let foodQuantity;
    // Form values
    let errorMsg;
    let errorMsg2;
    /** @type {{foodTruckName: int, customerUsername: string, foodNames: string}} */
    let selectedOrder = {orderID: null, customerUsername: null, foodNames: null};
    onMount(async () => {
        await fetchOrders();
    });
    async function fetchOrders() {
        try {
            const json = (await axios.get('http://localhost:4000/cus_order', {
                params: { customerUsername: $storeUsername, token: $token }
            })).data;
            if (json.error) {
                errorMsg = json.error
            } else {
                /** @type {[{orderID: int, customerUsername: string, foodNames: string}]} */
                order = json.filter(order => Object.keys(order).length !== 0);
            }
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
        {#if orders}
            {#each orders as order}
                <tr>
                    <td>
                        <label>
                            <input type="radio" bind:value={{ Date: order.orderDate }}/>
                            {order.Date}
                        </label>
                    </td>
                    <td>{order.orderID}</td>
                    <td>{order.orderTotal}</td>
                    <td>{order.foods}</td>
                    <td>{order.foodQuantity}</td>
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
