<!-- Screen 1: Login -->

<script>
    export let username;
    export let password;
</script>

<svelte:head>
    <title>Food Truck Login</title>
</svelte:head>

<h1>GT Food Truck</h1>

<form class="form">
    <label for="username">Username:</label>
    <input type="text" id="username" name="username" bind:value={$username} />
    <label for="password">Password:</label>
    <input type="text" id="password" name="password" bind:value={$password} />
</form>

<style>
  .form {
    display: grid;
    grid-template-columns: 20% 80%;
    grid-column-gap: 10px;
  }
</style>