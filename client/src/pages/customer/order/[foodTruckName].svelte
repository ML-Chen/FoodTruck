<!-- Screen #18 Customer Order -->

<script>
    import { onMount } from 'svelte';
    import { token, userType, storeUsername } from '../../_store.js';
    import { url, goto } from '@sveltech/routify';
    import axios from 'axios';

    token.useLocalStorage();
    userType.useLocalStorage();
    storeUsername.useLocalStorage();

    export let foodTruckName;
    foodTruckName = decodeURIComponent(foodTruckName);

    // Data fetched from the database
    /** @type {[{foodTruckName: string, stationName: string, foodName: string, price: decimal}]} */
    let foods = [];
    /** @type {[{foodTruckName: string, stationName: string, foodName: string, price: decimal}]} */
    let selected = [];
    let date;

    // Form values
    let errorMsg;
    onMount(async () => {
        await fetchTrucks();
    });
    async function fetchTrucks() {
        try {
            /** @type {[{foodTruckName: string, stationName: string, foodName: string, price: decimal}]} */
            foods = (await axios.get('http://localhost:4000/mn_view_foodTruck_menu', {
                params: { foodTruckName, token: $token }
            })).data;
            errorMsg = null;
        } catch (error) {
            console.log(error.response.data);
            errorMsg = error.response.data.error;
        }
    }
    async function placeOrder() {
        if (!selected.some(food => food)) {
            errorMsg = "You haven't selected any food to order"
        } else if (selected.some(food => !food.purchaseQuantity)) {
            errorMsg = "You can't select a zero quantity of something"
        } else if (!date) {
            errorMsg = "Please select an order date"
        } else {
            try {
                const orderID = (await axios.post('http://localhost:4000/cus_order', { date, customerUsername: $storeUsername, token: $token })).data.orderID;
                console.log(selected);
                for (const { foodName, purchaseQuantity } of selected) {
                    console.log({ foodTruckName, foodName, purchaseQuantity, orderID, token: $token })
                    await axios.post('http://localhost:4000/cus_add_item_to_order', { foodTruckName, foodName, purchaseQuantity, orderID, token: $token });
                }
            } catch (error) {
                console.log(error.response.data);
                errorMsg = error.response.data.error;
            }
        }
    }
  
</script>
  
<svelte:head>
    <title>Order</title>
</svelte:head>

<h1>Order</h1>

<p>Food Truck: {foodTruckName}</p>

<table>
    <thead>
        <tr>
            <td></td>
            <td>Food</td>
            <td>Price</td>
            <td>Purchase Quantity</td>
        </tr>
    </thead>
    <tbody>
        <!-- TODO -->
        {#each foods as food}
            <tr>
                <td><input type="checkbox" value={food} bind:group={selected} /></td>
                <td>{food.foodName}</td>
                <td>{food.price}</td>
                <td><input type="number" min="0" step="1" pattern="\d+" id="purchaseQuantity" name="purchaseQuantity" bind:value={food.purchaseQuantity} /></td>
            </tr>
        {/each}
    </tbody>
</table>
{#if errorMsg}
    <p class="error">{errorMsg}</p>
{/if}

<label for="Date">Order date</label>
<input type="Date" id="Date" name="Date" bind:value={date} aria-label="Date" />


<a href={$url('../../current-info')}>Back</a>
<button type="button" on:click={placeOrder}>Submit</button>
<style>
    .error {
        color: red;
    }
</style>
