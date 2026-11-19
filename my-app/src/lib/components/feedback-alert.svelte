<script lang="ts">
    let { message, variant = 'info', role = 'status' }: {
        message: string;
        variant?: 'success' | 'danger' | 'warning' | 'info';
        role?: 'alert' | 'status';
    } = $props();
</script>

<div class="alert alert-{variant} mb-3" {role}>{message}</div>
