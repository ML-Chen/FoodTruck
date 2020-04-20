<!-- Screen 10: Create Food -->
<script>
    import { url, goto } from '@sveltech/routify';
    import { token, userType } from '../_store.js';
    import axios from 'axios';

    token.useLocalStorage();
    userType.useLocalStorage();

    let FoodName;
    let errorMsg;

    async function createBuilding() {
        if (!FoodName) {
            errorMsg = 'Food name must not be blank';
        } else {
            try {
                const json = (await axios.post('http://localhost:4000/ad_create_food', { FoodName, token: $token })).data;
                    if (json.error) {
                        errorMsg = json.error;
                    } else {
                    }
            } catch (error) {
                console.log(error);
                errorMsg = 'Maybe the server is down?'
            }
        }
    }
</script>

    </script>

<svelte:head>
    <title>Create Food</title>
</svelte:head>


<h1>Create Food</h1>

<form on:submit|preventDefault={createFood}>
    <label for="FoodName">Name</label>
    <input type="text" id="FoodName" name="FoodName" bind:value={FoodName} />

    
    <button type="submit">Create</button>
</form>

<a href={$url('../../home')}>Back</a>