<!-- Screen 3: Home Screen -->

<script>
    import { userType } from './_store.js';
    import { url } from '@sveltech/routify';

    userType.useLocalStorage();
</script>

<svelte:head>
    <title>Food Truck Home</title>
</svelte:head>

<h1>Home</h1>

{#if $userType.includes('Customer')}
    <a href={$url('../customer/explore')}>Explore</a>
    <a href={$url('../customer/order-history')}>View order history</a>
    <a href={$url('../customer/current-info')}>View current customer info</a>
{/if}
{#if $userType.includes('Manager')}
    <a href={$url('../manager/manage-food-truck')}>Manage food truck</a>
    <a href={$url('../manager/food-truck-summary')}>View food truck summary</a>
{/if}
{#if $userType.includes('Admin')}
    <a href={$url('../admin/manage-building-station')}>Manage buildings and stations</a>
    <a href={$url('../admin/manage-food')}>Manage food</a>
{/if}
{#if !$userType.includes('Customer') && !$userType.includes('Manager') && !$userType.includes('Admin')}
    <p>You’re doing great! There’s nothing you need to do.</p>
{/if}

<style>
a {
    display: block;
}
</style>