<!-- Screen 10: Create Food -->

import { url, goto } from '@sveltech/routify';
    import { token, userType } from '../_store.js';
    import axios from 'axios';

    token.useLocalStorage();
    userType.useLocalStorage();

    </script>

<svelte:head>
    <title>Create Food</title>
</svelte:head>


<h1>Create Food</h1>

<form on:submit|preventDefault={createBuilding}>
    <label for="FoodName">Name</label>
    <input type="text" id="FoodName" name="FoodName" bind:value={FoodName} />

    
    <button type="submit">Create</button>
</form>

<a href={$url('../../home')}>Back</a>