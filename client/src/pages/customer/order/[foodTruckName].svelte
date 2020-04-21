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
    let foods = [];
    let price;
    let purchaseQuantity;
    let orderID;
    let date;

    // Form values
    let errorMsg;
    onMount(async () => {
        await fetchTrucks();
    });
    async function fetchTrucks() {
        try {
            const json = (await axios.get('http://localhost:4000/cus_current_information_foodTruck', {
                params: { customerUsername: $storeUsername, token: $token }
            })).data;
            if (json.error) {
                errorMsg = json.error
            } else {
                /** @type {[{foodTruckName: string, customerUsername: string, foodNames: string}]} */
                foodTrucks = json.filter(foodTruck => Object.keys(foodTruck).length !== 0);
            }
            errorMsg = null;
        } catch (error) {
            console.log(error.response.data);
            errorMsg = error.response.data.error;
        }
    }
    async function placeOrder() {
        try {
            const json = (await axios.get('http://localhost:4000/cus_order'), {
            // TODO
            })
        } catch (error) {
            console.log(error.response.data);
            errorMsg = error.response.data.error;
        }
    }
  
</script>
  
<svelte:head>
    <title>Order</title>
</svelte:head>


<h1>Order</h1>

<p>Food Truck: {foodTruckName}</p>

    <br>
    {#if errorMsg}
        <p class="error">{errorMsg}</p>
    {/if}

<table>
    <thead>
        <tr>
            <td>Food</td>
            <td>Price</td>
            <td>Purchase Quantity</td>
        </tr>
    </thead>
    <tbody>
        <!-- TODO -->
        {#each foods as food}
            <tr>
                <td>
                    <label>
                        <input type="checkbox" />
                        {food.foodName}
                    </label>
                </td>
                <td>{food.price}</td>
                <td><input type="purchaseQuantity" id="purchaseQuantity" name="purchaseQuantity" bind:value={purchaseQuantity} aria-label="purchaseQuantity" /></td>
            </tr>
        {/each}
    </tbody>
</table>
{#if errorMsg}
    <p class="error">{errorMsg}</p>
{/if}
 
<input type="Date" id="Date" name="Date" bind:value={date} aria-label="Date" />

<a href={$url('../../home')}>Back</a>
<button type="button" on:click={placeOrder}>Submit</button>
<style>
    .error {
        color: red;
    }
</style>
