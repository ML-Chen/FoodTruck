<script>
    import { userType } from '../_store';
    import { goto } from '@sveltech/routify';
    userType.useLocalStorage();
</script>

{#if $userType && $userType.includes('Manager')}
<slot>
  <!-- pages in this folder and subfolders
   will be rendered here -->
</slot>
{:else}
    {$goto('../../home')}
{/if}
