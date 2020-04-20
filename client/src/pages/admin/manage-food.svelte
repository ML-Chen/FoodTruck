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
    let sortedBy = 'name'; // choices: ['name', 'menuCount', 'purchaseCount']
    let sortDirection = 'ASC'; // choices: ['ASC', 'DESC']
    let selectedFoodName;

    onMount(fetchFoods);

    async function fetchFoods() {
        try {
            const json = (await axios.get('http://localhost:4000/ad_filter_food', {
                params: { foodName: foodNameFilter, sortedBy, sortDirection, token: $token }
            })).data;
            if (json.error) {
                errorMsg = json.error
            } else {
                foods = json.filter(food => Object.keys(food).length !== 0);
            }
            errorMsg = null;
        } catch (error) {
            errorMsg = error.response.data.error;
        }
    }

    async function deleteFood() {
        try {
            const json = (await axios.post('http://localhost:4000/ad_delete_food', {foodName: selectedFoodName, token: $token})).data;
            if (json.error) {
                errorMsg = json.error;
            } else {
                await fetchFoods();
            }
        } catch (error) {
            if (error.response.data.error.includes('IntegrityError')) {
                errorMsg = "This food can't be deleted because something depends on it";
            } else {
                errorMsg = error.response.data.error;
            }
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

    <label for="sort-by">Sort by:</label>
    <select id="sort-by" bind:value={sortedBy}>
        <option value="name">Name</option>
        <option value="menuCount">Menu count</option>
        <option value="purchaseCount">Purchase count</option>
    </select>

    <label for="sort-dir">Sort by:</label>
    <select id="sort-dir" bind:value={sortDirection}>
        <option value="ASC">Ascending</option>
        <option value="DESC">Descending</option>
    </select>

    <br>
    <button type="submit">Filter</button>
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
                    <tr>
                        <td>
                            <label>
                                <input type="radio" bind:group={selectedFoodName} value={food.foodName}/>
                                {food.foodName}
                            </label>
                        </td>
                        <td>{food.menuCount}</td>
                        <td>{food.purchaseCount}</td>
                    </tr>
                {/each}
            {/if}
        </tbody>
    </table>
    {#if errorMsg}
        <p class="error">{errorMsg}</p>
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