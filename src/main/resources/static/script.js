// CONFIGURACIÓN: Cambia esto por tu URL de Render (ej: "https://secure-devops-pipeline-1.onrender.com")
const API_BASE_URL = "https://secure-devops-pipeline-1.onrender.com";

// Elementos del DOM
const statusIndicator = document.getElementById("status-indicator");
const userForm = document.getElementById("user-form");
const usersTableBody = document.querySelector("#users-table tbody");
const formMessage = document.getElementById("form-message");

// Elementos dinámicos del formulario para el modo Edición
const usuarioIdInput = document.getElementById("usuario-id");
const nombreInput = document.getElementById("nombre");
const emailInput = document.getElementById("email");
const formTitle = document.getElementById("form-title");
const btnSubmit = document.getElementById("btn-submit");
const btnCancel = document.getElementById("btn-cancel");

let modoEdicion = false;

// --- 1. CONSULTAR EL ESTADO (GET /health) ---
async function checkSystemHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            statusIndicator.textContent = "En línea";
            statusIndicator.className = "status-badge status-ok";
        } else {
            throw new Error();
        }
    } catch (error) {
        statusIndicator.textContent = "No disponible";
        statusIndicator.className = "status-badge status-error";
    }
}

// --- 2. OBTENER USUARIOS (GET /usuarios) ---
async function fetchUsuarios() {
    try {
        const response = await fetch(`${API_BASE_URL}/usuarios`);
        if (!response.ok) throw new Error("Error en la petición");

        const usuarios = await response.json();
        usersTableBody.innerHTML = "";

        if (usuarios.length === 0) {
            usersTableBody.innerHTML = `<tr><td colspan="4" class="text-center text-muted">No hay pacientes registrados.</td></tr>`;
            return;
        }

        usuarios.forEach(usuario => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td><strong>${usuario.id}</strong></td>
                <td>${escapeHTML(usuario.nombre)}</td>
                <td>${escapeHTML(usuario.email)}</td>
                <td>
                    <button class="btn-action btn-edit" onclick="prepararEdicion(${usuario.id})">Editar</button>
                    <button class="btn-action btn-delete" onclick="eliminarUsuario(${usuario.id})">Eliminar</button>
                </td>
            `;
            usersTableBody.appendChild(row);
        });
    } catch (error) {
        console.error("Error al listar usuarios:", error);
        usersTableBody.innerHTML = `<tr><td colspan="4" class="text-center" style="color: red;">Error al conectar con la base de datos de usuarios.</td></tr>`;
    }
}

// --- 3. PROCESAR FORMULARIO (POST para crear / PUT para actualizar) ---
userForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const id = usuarioIdInput.value;
    const nombre = nombreInput.value.trim();
    const email = emailInput.value.trim();

    const datosUsuario = { nombre, email };
    
    // Determinar URL y método HTTP según corresponda
    const url = modoEdicion ? `${API_BASE_URL}/usuarios/${id}` : `${API_BASE_URL}/usuarios`;
    const metodo = modoEdicion ? "PUT" : "POST";

    showMessage("", false);

    try {
        const response = await fetch(url, {
            method: metodo,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(datosUsuario)
        });

        if (response.ok || response.status === 201) {
            showMessage(modoEdicion ? "Paciente actualizado correctamente." : "Paciente registrado con éxito.", true);
            cancelarEdicion();
            fetchUsuarios();
        } else {
            throw new Error();
        }
    } catch (error) {
        console.error("Error en el formulario:", error);
        showMessage("Ocurrió un error al procesar la solicitud. Verifica los campos.", false);
    }
});

// --- 4. PREPARAR FORMULARIO PARA EDITAR (GET /usuarios/{id}) ---
async function prepararEdicion(id) {
    try {
        const response = await fetch(`${API_BASE_URL}/usuarios/${id}`);
        if (!response.ok) throw new Error();

        const usuario = await response.json();

        // Cargar los datos devueltos en el formulario
        usuarioIdInput.value = usuario.id;
        nombreInput.value = usuario.nombre;
        emailInput.value = usuario.email;

        // Cambiar interfaz al modo edición
        modoEdicion = true;
        formTitle.textContent = "Actualizar Paciente";
        btnSubmit.textContent = "Guardar cambios";
        btnCancel.classList.remove("hidden");
        
        nombreInput.focus();
    } catch (error) {
        console.error("Error al obtener usuario:", error);
        showMessage("No se pudieron cargar los datos del usuario.", false);
    }
}

// --- 5. ELIMINAR USUARIO (DELETE /usuarios/{id}) ---
async function eliminarUsuario(id) {
    if (!confirm(`¿Confirmar eliminación del paciente con ID ${id}?`)) return;

    try {
        const response = await fetch(`${API_BASE_URL}/usuarios/${id}`, {
            method: "DELETE"
        });

        if (response.ok || response.status === 204) {
            showMessage("Paciente eliminado correctamente.", true);
            if (modoEdicion && usuarioIdInput.value == id) cancelarEdicion();
            fetchUsuarios();
        } else {
            throw new Error();
        }
    } catch (error) {
        console.error("Error al eliminar:", error);
        showMessage("No se pudo eliminar el usuario.", false);
    }
}

// --- FUNCIONES HELPER ---
function cancelarEdicion() {
    modoEdicion = false;
    userForm.reset();
    usuarioIdInput.value = "";
    formTitle.textContent = "Nuevo Paciente";
    btnSubmit.textContent = "Registrar paciente";
    btnCancel.classList.add("hidden");
}

btnCancel.addEventListener("click", cancelarEdicion);

function showMessage(text, isSuccess) {
    if (!text) {
        formMessage.className = "message hidden";
        return;
    }
    formMessage.textContent = text;
    formMessage.className = `message ${isSuccess ? 'success' : 'error'}`;
}

function escapeHTML(str) {
    return str.replace(/[&<>'"]/g, 
        tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
    );
}

// --- INICIALIZACIÓN ---
document.addEventListener("DOMContentLoaded", () => {
    checkSystemHealth();
    fetchUsuarios();
    setInterval(checkSystemHealth, 30000);
});