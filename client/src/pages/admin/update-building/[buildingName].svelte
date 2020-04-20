<!-- Screen 6: Update Building -->

<script>
    import { onMount } from 'svelte';
    import { url, goto } from '@sveltech/routify';
    import { token, userType } from '../../_store.js';
    import axios from 'axios';

    token.useLocalStorage();
    userType.useLocalStorage();

    export let buildingName;
    const oldBuildingName = decodeURIComponent(buildingName);
    let newBuildingName = oldBuildingName;
    let description;
    let tags = [];
    let wipTag;
    let tagsAdded = [];
    let tagsRemoved = [];
    let errorMsg;

    onMount(async () => {
        await fetchBuilding();
        await fetchTags();
        console.log(tags);
    });

    async function fetchBuilding() {
        try {
            const json = (await axios.get('http://localhost:4000/ad_view_building_general', {
                params: { buildingName: oldBuildingName, token: $token }
            })).data;
            if (json.error) {
                errorMsg = json.error
            } else {
                newBuildingName = json.buildingName;
                description = json.description;
                errorMsg = null;
            }
        } catch (error) {
            console.log(error);
            errorMsg = error;
        }
    }
    async function fetchTags() {
        try {
            const json = (await axios.get('http://localhost:4000/ad_view_building_tags', {
                params: { buildingName: oldBuildingName, token: $token }
            })).data;
            if (json.error) {
                errorMsg = json.error;
            } else {
                tags = json.map(obj => obj.tag);
            }
        } catch (error) {
            console.log(error.response.data);
            errorMsg = error.response.data.error;
        }
    }
    async function updateBuilding() {
        try {
            const json = (await axios.post('http://localhost:4000/ad_update_building', { oldBuildingName, newBuildingName, description, token: $token })).data;
                if (json.error) {
                    errorMsg = json.error;
                } else {
                    for (let tag of tagsAdded) {
                        await axios.post('http://localhost:4000/ad_add_building_tag', { buildingName, tag, token: $token })
                    }
                    for (let tag of tagsRemoved) {
                        await axios.post('http://localhost:4000/ad_remove_building_tag', { buildingName, tag, token: $token })
                    }
                }
        } catch (error) {
            console.log(error.response.data);
            errorMsg = error.response.data.error;
        }
    }
</script>

<svelte:head><title>Update Building</title></svelte:head>

<h1>Update Building</h1>

<form on:submit|preventDefault={updateBuilding}>
    <label for="buildingName">Name</label>
    <input type="text" id="buildingName" name="buildingName" bind:value={newBuildingName} />

    <label for="description">Description</label>
    <textarea id="description" name="description" bind:value={description} />

    <label for="tags">Tags</label>
        {#each tags as tag, index (tag)}
            <button type="button" on:click={() => {
                tags = tags.filter((_, i) => i !== index);
                tagsRemoved = tagsRemoved.concat(tag)
            }} aria-label="Remove tag {tag}">−</button>{tag}<br />
        {/each}
    <button type="button" on:click={() => {
        if (wipTag) {
            tags = tags.concat(wipTag);
            tagsAdded = tagsAdded.concat(wipTag);
            wipTag='';
        }
    }} aria-label="Add tag {wipTag}">+</button>
    <input type="text" bind:value={wipTag} /><br />
    <button type="submit">Update</button>
</form>

{#if errorMsg}
    <p class="errorMsg">{errorMsg}</p>
{/if}

<a href={$url('../../manage-building-station')}>Back</a>

<style>
    .errorMsg {
        color: red;
    }
</style>