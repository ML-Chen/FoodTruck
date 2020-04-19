<!-- Screen 1: Login -->

<script>
    import { setContext } from 'svelte';
    import wretch from 'wretch';

    let username;
    let password;
    let errorMsg;

    export async function handleLogin() {
        const response = await fetch('http://127.0.0.1:4000/login', {
            method: 'POST',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        const json = await response.json();
        if (json === []) {
            errorMsg = 'Username and/or password incorrect';
        } else if (json.error) {
            errorMsg = json.error;
        } else {
            setContext('token', json.token);
            setContext('userType', json.userType);
        }
    }
</script>

<svelte:head>
    <title>Food Truck Login</title>
</svelte:head>

<h1>GT Food Truck</h1>

<form class="form" on:submit|preventDefault={handleLogin}>
    <label for="username">Username:</label>
    <input type="text" id="username" name="username" bind:value={username} />
    <label for="password">Password:</label>
    <input type="text" id="password" name="password" bind:value={password} />
    <button type="submit">Login</button>
    <button type="button">Register</button>
    {#if errorMsg}
        <p class="error">{errorMsg}</p>
    {/if}
</form>

<style>
    .error {
        color: red;
    }
</style>