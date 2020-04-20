<!-- Screen 4: Admin Manage Building & Station -->

<script>
    import { onMount } from 'svelte';
    import { token, userType } from '../_store.js';
    import { url, goto } from '@sveltech/routify';
    import axios from 'axios';

    token.useLocalStorage();
    userType.useLocalStorage();

    // Data fetched from the database
    /** @type {[{foodName: string, menuCount: number, purchaseCount: number, }]} */
    let foods;

    // Form values (all strings)
    let errorMsg;
    let errorMsg2;
    let foodNameFilter;
    let selectedFoodName;

    onMount(fetchFoods);

    async function fetchFoods() {
        try {
            const json = (await axios.get('http://localhost:4000/ad_filter_food', {
                params: { foodName: foodNameFilter }
            })).data;
            if (json.error) {
                errorMsg = json.error
            } else {
                foods = json.filter(food => Object.keys(food).length !== 0);
            }
            errorMsg = null;
            errorMsg2 = null;
        } catch (error) {
            console.log(error);
            errorMsg = 'Network error. Maybe the server is down?';
        }
    }

    async function deleteFood() {
        try {
            const json = (await axios.post('http://localhost:4000/ad_delete_food', {foodName: selectedFoodName})).data;
            if (json.error) {
                errorMsg = json.error;
            } else {
                await fetchFoods();
            }
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

<form on:submit|preventDefault={fetchFoods}>
    <label for="food-name">Name</label>
    <input type="text" id="food-name" name="food-name" bind:value={foodNameFilter} />

    <br>
    <button type="submit">Filter</button>
    {#if errorMsg}
        <p class="error">{errorMsg}</p>
    {/if}
</form>

<form on:submit|preventDefault={deleteFood}>
    <table>
        <thead>
            <tr>
                <td>Name</td>
                <td>Menu Count</td>
                <td>Purchase Count</td>
            </tr>
        </thead>
        <tbody>
            {#if foods}
                {#each foods as food}
                    <td>
                        <label>
                            <input type="radio" bind:group={selectedFoodName} value={food.foodName}/>
                        </label>
                        {food.foodName}
                    </td>
                    <td>{food.menuCount}</td>
                    <td>{food.purchaseCount}</td>
                {/each}
            {/if}
        </tbody>
    </table>
    {#if errorMsg2}
        <p class="error">{errorMsg2}</p>
    {/if}

    <a href={$url('../create-food')}>Create food</a>
    <button type="submit" on:click={deleteFood}>Delete food</button>
</form>

<a href={$url('../../home')}>Back</a>


<style>
    .error {
        color: red;
    }
</style>