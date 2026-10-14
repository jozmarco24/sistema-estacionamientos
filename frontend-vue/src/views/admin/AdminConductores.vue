<template>
  <div class="section-view active-section">
    <div class="card">
      <h2 class="card-title"><i class="fa-solid fa-users"></i> Conductores Registrados</h2>
      <div class="table-wrapper" style="max-height: 500px;">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Nombre Completo</th>
              <th>Correo Electrónico</th>
              <th>Estado de Cuenta</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in conductoresList" :key="c.id">
              <td>#{{ c.id }}</td>
              <td>{{ c.nombre }}</td>
              <td>{{ c.email }}</td>
              <td>
                <span class="status-badge" :class="c.activo ? 'libre' : 'ocupado'">
                  {{ c.activo ? 'Activo' : 'Inactivo' }}
                </span>
              </td>
            </tr>
            <tr v-if="conductoresList.length === 0">
              <td colspan="4" style="text-align: center; color: var(--text-muted);">No hay conductores registrados.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  conductoresList: { type: Array, default: () => [] }
})
</script>
