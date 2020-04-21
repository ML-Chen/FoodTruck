<!-- Screen 10: Create Food -->
<script>
    import { url, goto } from '@sveltech/routify';
    import { token, userType } from '../_store.js';
    import axios from 'axios';

    token.useLocalStorage();
    userType.useLocalStorage();

    let foodName;
    let errorMsg;

    async function createFood() {
        if (!foodName) {
            errorMsg = 'Food name must not be blank';
        } else {
            try {
                const json = (await axios.post('http://localhost:4000/ad_create_food', { foodName, token: $token })).data;
                if (json.error) {
                    errorMsg = json.error;
                } else {
                    foodName = errorMsg = '';
                }
            } catch (error) {
                console.log(error.response.data)
                errorMsg = error.response.data.error;
            }
        }
    }
</script>

<svelte:head>
    <title>Create Food</title>
</svelte:head>


<h1>Create Food</h1>

<form on:submit|preventDefault={createFood}>
    <label for="foodName">Name</label>
    <input type="text" id="foodName" name="foodName" bind:value={foodName} />

    <button type="submit">Create</button>
</form>

<a href={$url('../manage-food')}>Back</a>