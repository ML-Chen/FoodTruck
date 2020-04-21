<!-- Screen 2: Register -->
<script>
    import { url, goto } from '@sveltech/routify';
    import axios from 'axios';
    let username;
    let email;
    let firstName;
    let lastName;
    let password;
    let confirmPassword;
    let balance;
    let type;
    let errorMsg;

    export async function handleRegister() {
        console.log(type)
        if (password.length < 8) {
            errorMsg = 'Password must be greater 8 characters'
        } else if (password != confirmPassword) {
            errorMsg = 'Confirm password must match password'
        } else if (!type && email) {
            errorMsg = "If you have an email, you must select a type of employee to be"
        } else if (balance && balance <= 0) {
            errorMsg = 'Balance must be a positive number'
        } else if (!type && (!balance || balance <= 0)) {
            errorMsg = "If you're not an employee, you must have a positive balance"
        } else if (!(/\b[A-z0-9._%+-]+@[A-z0-9.-]+\.[A-z]{2,}\b/.test(email)) {
            errorMsg = "Email must be in ____@__.___ format"
        } else {
            const response = await axios.post('http://127.0.0.1:4000/register', { username, email, firstName, lastName, password, balance, type: email ? type : null });
            const json = response.data;
            if (json === []) {
                errorMsg = 'Error';
            } else if (json.error) {
                errorMsg = json.error;
            } else {
                console.log("Success");
                $goto('../login')
            }
        }
    }


</script>

<svelte:head>
    <title>Food Truck Register</title>
</svelte:head>

<h1>Register</h1>

<form class="form" on:submit|preventDefault={handleRegister}>
    <label for="username">Username</label>
    <input type="text" id="username" name="username" bind:value={username} />
    <label for="email">Email</label>
    <input type="text" id="email" name="email" bind:value={email} />
    <label for="firstName">First Name</label>
    <input type="text" id="firstName" name="firstName" bind:value={firstName} />
    <label for="lastName">Last Name</label>
    <input type="text" id="lastName" name="lastName" bind:value={lastName} />
    <label for="password">Password</label>
    <input type="password" id="password" name="password" bind:value={password} />
    <label for="confirmPassword">Confirm Password</label>
    <input type="password" id="confirmPassword" name="confirmPassword" bind:value={confirmPassword} />
    <label for="balance">Balance</label>
    <input type="number" id="balance" name="balance" bind:value={balance} />
    <br />

    {#if email}
        <input type="radio" id="admin" name="type" value="Admin" bind:group={type}>
        <label for="admin" class="radio">Admin</label>

        <input type="radio" id="manager" name="type" value="Manager" bind:group={type}>
        <label for="manager" class="radio">Manager</label>

        <input type="radio" id="staff" name="type" value="Staff" bind:group={type}>
        <label for="staff" class="radio">Staff</label>
    {/if}
    
    <br />

    <button type="submit">Register</button>
    {#if errorMsg}
        <p class="error">{errorMsg}</p>
    {/if}
</form>
<a href={$url('../index')}>Back</a>

<style>
    label.radio {
        display: inline;
    }
    .error {
        color: red;
    }
</style>
