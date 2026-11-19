<script lang="ts">
    let { title, description = '', eyebrow = '' }: {
        title: string;
        description?: string;
        eyebrow?: string;
    } = $props();
</script>

<header class="page-header mb-4">
    {#if eyebrow}<p class="small text-uppercase text-muted fw-semibold mb-1">{eyebrow}</p>{/if}
    <h1 class="h2 fw-bold mb-1">{title}</h1>
    {#if description}<p class="text-muted mb-0">{description}</p>{/if}
</header>
