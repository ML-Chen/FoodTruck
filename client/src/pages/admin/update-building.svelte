<!-- Screen 6: Update Building -->

<script>
    import { url, goto } from '@sveltech/routify';
    import { token, userType } from '../_store.js';
    import axios from 'axios';

    token.useLocalStorage();
    userType.useLocalStorage();

    let buildingName;
    let description;
    let tags = [];
    let wipTag;
    let errorMsg;

    async function updateBuilding() {
        try {
            const json = (await axios.post('http://localhost:4000/ad_update_building', { buildingName, description, token: $token })).data;
                if (json.error) {
                    errorMsg = json.error;
                } else {
                    for (let tag of tags) {
                        axios.post('http://localhost:4000/ad_add_building_tag', { buildingName, tag, token: $token })
                    }
                    buildingName = description = wipTag = errorMsg = '';
                    tags = [];
                }
        } catch (error) {
            console.log(error);
            errorMsg = 'Maybe the server is down?'
        }
    }
</script>

<svelte:head>Update Building</svelte:head>

<h1>Update Building</h1>

<form on:submit|preventDefault={updateBuilding}>
    <label for="buildingName">Name</label>
    <input type="text" id="buildingName" name="buildingName" bind:value={buildingName} />

    <label for="description">Description</label>
    <textarea id="description" name="description" bind:value={description} />

    <label for="tags">Tags</label>
        {#each tags as tag, index (tag)}
            <button type="button" on:click={() => { tags = tags.filter((_, i) => i !== index) }} aria-label="Remove tag {tag}">−</button>{tag}<br />
        {/each}
    <button type="button" on:click={() => { if (wipTag) { tags = tags.concat(wipTag); wipTag=''; }}} aria-label="Add tag {wipTag}">+</button>
    <input type="text" bind:value={wipTag} /><br />
    <button type="submit">Update</button>
</form>

<a href={$url('../../home')}>Back</a>
