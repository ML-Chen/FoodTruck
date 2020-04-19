<script>
    import { userType } from './_store.js';
    import { url } from '@sveltech/routify';

    userType.useLocalStorage();
</script>

<svelte:head>
    <title>Food Truck</title>
</svelte:head>

<h1>Food Truck</h1>

<p>The best app for buying food from food trucks (or even managing your food truck)! Cybernetically powered by Svelte, Routify, Flask, and MySQL.</p>

{#if !userType}
    <p>Why don't you <a href={$url('../login')}>log in</a> or <a href={$url('../register')}>create an account</a>?</p>
{:else if userType === 'Staff'}
    <p>Hi staff member, you’re doing great work!</p>
{:else}
    <p>Check out your slick <a href={$url('../home')}>personal dashboard</a>!</p>
{/if}