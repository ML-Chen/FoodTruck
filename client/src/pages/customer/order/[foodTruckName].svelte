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
    let foods = []; // [{foodTruckName: string, stationName: string, foodName: string, price: decimal}]
    let selectedFoodNames = []; // string[], list of food names
    let date;

    let balance;
    let orderTotal = (0).toFixed(2);

    function calculateOrderTotal() {
        orderTotal = foods.reduce((currentVal, food) => !food.purchaseQuantity || !selectedFoodNames.includes(food.foodName) ? currentVal : currentVal + food.price * food.purchaseQuantity, 0).toFixed(2);
    }

    // Form values
    let errorMsg;
    onMount(async () => {
        await fetchFoods();
        await fetchBalance();
    });
    async function fetchFoods() {
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
    async function fetchBalance() {
        try {
            balance = (await axios.get('http://localhost:4000/cus_current_information_basic', {
                params: { customerUsername: $storeUsername, token: $token }
            })).data.balance;
        } catch (error) {
            console.log(error.response.data);
            errorMsg = error.response.data.error;
        }
    }
    async function placeOrder() {
        const selected = foods.filter(food => selectedFoodNames.includes(food.foodName));
        console.log(selected);
        if (orderTotal && orderTotal - balance >= 0) {
            // orderTotal > balance was erroneously returning true for some reason
            errorMsg = 'Your order total is greater than your balance';
        } else if (!selected.some(food => food)) {
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
                await fetchBalance();
                errorMsg = null;
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

<p>Balance: {balance}</p>

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
        {#if foods}
            {#each foods as food}
            <tr>
                <td>
                    <label>
                        <input type="checkbox" value={food.foodName} bind:group={selectedFoodNames} on:change={calculateOrderTotal} />
                        {food.foodName}
                    </label>    
                </td>
                <td>{food.price}</td>
                <td><input type="number" min="0" step="1" pattern="\d+" id="purchaseQuantity" name="purchaseQuantity" bind:value={food.purchaseQuantity} on:input={calculateOrderTotal} /></td>
            </tr>
            {/each}
        {/if}        
    </tbody>
</table>

<label for="Date">Order date</label>
<input type="Date" id="Date" name="Date" bind:value={date} aria-label="Date" />

<p>Order total: {orderTotal}</p>

{#if errorMsg}
    <p class="error">{errorMsg}</p>
{/if}

<a href={$url('../../current-info')}>Back</a>
<button type="button" on:click={placeOrder}>Submit</button>
<style>
    .error {
        color: red;
    }
</style>
