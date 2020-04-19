<!-- Screen 1: Login -->

<script>
    import { setContext } from 'svelte';

    export let username;
    export let password;

    export async function handleLogin() {
        const response = await this.fetch('http://127.0.0.1:5000/login', {
            method: 'POST',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        const { token, userType, error } = await response.json();
        if (!error) {
            setContext('token', token);
            setContext('userType', userType);
        } else {
            console.log(error);
            alert(error);
        }
    }
</script>

<svelte:head>
    <title>Food Truck Login</title>
</svelte:head>

<h1>GT Food Truck</h1>

<form class="form" on:submit|preventDefault={handleLogin}>
    <label for="username">Username:</label>
    <input type="text" id="username" name="username" bind:value={$username} />
    <label for="password">Password:</label>
    <input type="text" id="password" name="password" bind:value={$password} />
    <button type="submit">Login</button>
    <button type="button">Register</button>
</form>
