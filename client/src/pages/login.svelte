<!-- Screen 1: Login -->

<script>
    import { token, userType, storeUsername } from './_store.js';
    import { url, goto } from '@sveltech/routify';

    token.useLocalStorage();
    userType.useLocalStorage();
    storeUsername.useLocalStorage();

    let username;
    let password;
    let errorMsg;

    async function handleLogin() {
        if (!username) {
            errorMsg = 'Username must not be blank';
        } else if (!password || password.length < 8) {
            errorMsg = 'Password must be at least 8 characters long'
        } else {
            try {
                const response = await fetch('http://127.0.0.1:4000/login', {
                    method: 'POST',
                    mode: 'cors',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ username, password })
                });
                const json = await response.json();
                console.log(json);
                if (json.length === 0) {
                    errorMsg = 'Username and/or password incorrect';
                } else if (json.error) {
                    errorMsg = json.error;
                } else {
                    token.set(json.token);
                    userType.set(json.userType);
                    storeUsername.set(json.username);
                    $goto('../home')
                }
            } catch (error) {
                console.log(error.response.data)
                errorMsg = error.response.data.error;
            }
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
    <input type="password" id="password" name="password" bind:value={password} />
    <br>
    <button type="submit">Login</button>
    <p>or <a href={$url('../register')}>Register</a></p>
    {#if errorMsg}
        <p class="error">{errorMsg}</p>
    {/if}
</form>

<style>
    .error {
        color: red;
    }
</style>